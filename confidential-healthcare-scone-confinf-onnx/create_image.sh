#!/bin/bash
#
# tasks performed:
#
# - creates a local Docker image with an encrypted Python program (flask patient service) and encrypted input file
# - pushes a new session to a CAS instance
# - creates a file with the session name
#
# show what we do (-x), export all varialbes (-a), and abort of first error (-e)

set -x -a -e
trap "echo Unexpected error! See log above; exit 1" ERR

# CONFIG Parameters (might change)

export IMAGE=${IMAGE:-flask_restapi_image}
export SCONE_CAS_ADDR="4-2-1.scone-cas.cf"
export DEVICE="/dev/sgx"
export FLASK_HOSTNAME=${FLASK_HOSTNAME:-api}

export CAS_MRENCLAVE="4cd0fe54d3d8d787553b7dac7347012682c402220acd062e4d0da3bbe10a1c2c"

export CLI_IMAGE="sconecuratedimages/sconecli:alpine3.7-scone4.2.1"
export PYTHON_IMAGE="sconecuratedimages/experimental:scone-run-ubuntu18.04-python3.8.1"
export PYTHON_MRENCLAVE="7f3bd1a74e8ed3355656c6e262f26955678421af99d2ca7b0b439eac565900a9"
export REDIS_IMAGE="sconecuratedimages/experimental:redis-6-ubuntu"
export REDIS_MRENCLAVE="60c87d30d609afd79d9c0af2b211ac30291d72e8989c1c6895d9aa3703b28882"

CONFONNX_DIR=${CONFONNX_DIR:-confonnx}
CONFONNX_WHEEL_FILENAME="confonnx-0.1.0-cp38-cp38-linux_x86_64.whl"
CONFONNX_WHEEL_PATH=$CONFONNX_DIR/dist/Release/lib/python/$CONFONNX_WHEEL_FILENAME

if [ ! -f $CONFONNX_WHEEL_PATH ]; then
    echo "$CONFONNX_WHEEL_PATH not found"
    exit 1
fi

docker pull $PYTHON_IMAGE
docker pull $REDIS_IMAGE

# create random and hence, uniquee session number
FLASK_SESSION="FlaskSession-$RANDOM-$RANDOM-$RANDOM"
REDIS_SESSION="RedisSession-$RANDOM-$RANDOM-$RANDOM"

# create directories for encrypted files and fspf
rm -rf encrypted-files
rm -rf native-files
rm -rf fspf-file

mkdir native-files/
mkdir encrypted-files/
mkdir fspf-file/
cp fspf.sh fspf-file
cp rest_api.py native-files/

if [ -d "$LETSENCRYPT_CERT_DIR" ]; then
    cp $LETSENCRYPT_CERT_DIR/*.pem native-files/
else
    echo "LETSENCRYPT_CERT_DIR not set! will use untrusted cert"
fi

# ensure that we have an up-to-date image
docker pull $CLI_IMAGE

# attest cas before uploading the session file, accept CAS running in debug
# mode (-d) and outdated TCB (-G)
docker run --device=$DEVICE -it $CLI_IMAGE sh -c "
scone cas attest -G --only_for_testing-debug  $SCONE_CAS_ADDR $CAS_MRENCLAVE >/dev/null \
&&  scone cas show-certificate" > cas-ca.pem

# create encrypte filesystem and fspf (file system protection file)
#docker run --device=$DEVICE  -it -v $(pwd)/fspf-file:/fspf/fspf-file -v $(pwd)/native-files:/fspf/native-files/ -v $(pwd)/encrypted-files:/fspf/encrypted-files $CLI_IMAGE /fspf/fspf-file/fspf.sh

# Copy confonnx client wheel for installation in image
cp $CONFONNX_WHEEL_PATH .

cat >Dockerfile <<EOF
FROM $CLI_IMAGE as cli

FROM $PYTHON_IMAGE as requirements
COPY requirements.txt requirements.txt
COPY $CONFONNX_WHEEL_FILENAME $CONFONNX_WHEEL_FILENAME
RUN pip --version
RUN pip install -r requirements.txt
RUN pip install $CONFONNX_WHEEL_FILENAME

FROM requirements as fspf
ENV SCONE_MODE=sim
COPY native-files /fspf/native-files/
COPY fspf.sh /fspf.sh
COPY --from=cli /opt/scone/bin /opt/scone/bin
COPY --from=cli /opt/scone/scone-cli /opt/scone/scone-cli
COPY --from=cli /usr/local/bin/scone /usr/local/bin/scone
RUN mkdir -p /fspf/fspf-file && mkdir -p /fspf/encrypted-files && /fspf.sh && \
    cat /fspf/native-files/keytag

FROM requirements
COPY --from=fspf /fspf/fspf-file/fs.fspf /fspf/fs.fspf
COPY --from=fspf /fspf/encrypted-files /fspf/encrypted-files

# Azure DCAP client
RUN apt-get update && apt-get -y install \
    software-properties-common apt-transport-https gnupg
RUN curl --retry 5 --retry-connrefused https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    apt-add-repository https://packages.microsoft.com/ubuntu/$(lsb_release -r -s)/prod && \
    apt-get update && \
    apt-get -y install --no-install-recommends \
    az-dcap-client
EOF

# create an image with encrypted flask service
output=$(docker build --no-cache --pull -t $IMAGE .)
echo $output
KEYTAG=$(printf "$output" | grep "key:")

# ensure that we have self-signed client certificate

if [[ ! -f client.pem || ! -f client-key.pem  ]] ; then
    openssl req -newkey rsa:4096 -days 365 -nodes -x509 -out client.pem -keyout client-key.pem -config clientcertreq.conf
fi

# create session file

export SCONE_FSPF_KEY=$(echo $KEYTAG | awk '{print $11}')
export SCONE_FSPF_TAG=$(echo $KEYTAG | awk '{print $9}')

MRENCLAVE=$REDIS_MRENCLAVE envsubst '$MRENCLAVE $REDIS_SESSION $FLASK_SESSION' < redis-template.yml > redis_session.yml
# note: this is insecure - use scone session create instead
curl -v -k -s --cert client.pem  --key client-key.pem  --data-binary @redis_session.yml -X POST https://$SCONE_CAS_ADDR:8081/session
MRENCLAVE=$PYTHON_MRENCLAVE envsubst '$MRENCLAVE $SCONE_FSPF_KEY $SCONE_FSPF_TAG $FLASK_SESSION $REDIS_SESSION $CONFONNX_URL $CONFONNX_API_KEY $AZ_APP_ID $AZ_APP_PWD $FLASK_HOSTNAME' < flask-template.yml > flask_session.yml
# note: this is insecure - use scone session create instead
curl -v -k -s --cert client.pem  --key client-key.pem  --data-binary @flask_session.yml -X POST https://$SCONE_CAS_ADDR:8081/session


# create file with environment variables

cat > myenv << EOF
export FLASK_SESSION="$FLASK_SESSION"
export REDIS_SESSION="$REDIS_SESSION"
export SCONE_CAS_ADDR="$SCONE_CAS_ADDR"
export IMAGE="$IMAGE"
export DEVICE="$DEVICE"

EOF

echo "OK"
