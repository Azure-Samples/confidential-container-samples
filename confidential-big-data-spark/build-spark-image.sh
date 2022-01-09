#!/bin/bash
#
# Access to this file is granted under the SCONE SOURCE CODE LICENSE V1.0
#
# Commercial use of any product using this file requires a commercial
# license from scontain UG, www.scontain.com.
#
# also see https://sconedocs.github.io
#
# Copyright (C) 2021 Scontain UG

# For more details, see SCONE Fileshield: https://sconedocs.github.io/SCONE_Fileshield/

# Remove files from previous build
rm -rf build

# Create build folders
mkdir -p build/policies build/kubernetes build/cas build/images/driver/fspf/encrypted-files build/images/executor

# Create base spark image
docker build . -t $SPARK_IMAGE-base -f Dockerfile

# Run scone fspf
# https://sconedocs.github.io/SCONE_Fileshield/
docker run --rm -t --entrypoint bash \
                -v "$PWD":/fspf \
                -v "$PWD"/build/images/driver/fspf:/out \
                $SPARK_IMAGE-base \
                /fspf/main_fspf.sh

# Generate encrypted scripts and libraries
docker run --rm -t --entrypoint bash \
                -v "$PWD"/input:/input \
                -v "$PWD":/script \
                -v "$PWD"/build/images/driver/fspf:/out \
                -v "$PWD"/build/images/driver/fspf:/fspf \
                $SPARK_IMAGE-base \
                /script/fspf.sh

# Copy volume.fspf
mv build/images/driver/fspf/volume.fspf build/images/driver/fspf/encrypted-files

# Generate Driver dockerfile from base image
echo "FROM $SPARK_IMAGE-base" > build/images/driver/Dockerfile
echo "ADD fspf/fspf.pb /" >> build/images/driver/Dockerfile
echo "ADD fspf/encrypted-files /fspf/encrypted-files" >> build/images/driver/Dockerfile

# Temporarily change directory to build Driver image - but this time with our encrypted files added
pushd build/images/driver
docker build . -t $SPARK_IMAGE
popd

# Generate environment variables for futher steps
cat > /tmp/env.sh <<EOF
export DRIVER_PYTHON_MRENCLAVE=$(docker run --rm -t --entrypoint bash -e SCONE_HASH=1 -e SCONE_HEAP=1G -e SCONE_MPROTECT=0 $SPARK_IMAGE -c "python3")

# Driver and executors have the same image, therefore the same MrEnclave...
export DRIVER_JAVA_MRENCLAVE=$(docker run --rm -t --entrypoint bash -e SCONE_HASH=1 $SPARK_IMAGE -c "/usr/lib/jvm/java-1.8-openjdk/bin/java")
export EXECUTOR_JAVA_MRENCLAVE=$(docker run --rm -t --entrypoint bash -e SCONE_HASH=1 $SPARK_IMAGE -c "/usr/lib/jvm/java-1.8-openjdk/bin/java")

export DRIVER_MAIN_FSPF_KEY=$(cat build/images/driver/fspf/main_fspf_keytag.txt | awk '{print $11}')
export DRIVER_MAIN_FSPF_TAG=$(cat build/images/driver/fspf/main_fspf_keytag.txt | awk '{print $9}')

export DRIVER_VOLUME_FSPF_KEY=$(cat build/images/driver/fspf/volume_keytag.txt | awk '{print $11}')
export DRIVER_VOLUME_FSPF_TAG=$(cat build/images/driver/fspf/volume_keytag.txt | awk '{print $9}')

export CAS_NAMESPACE="pyspark-azure-$RANDOM$RANDOM"
export PYSPARK_SESSION_NAME="pyspark"
EOF

sed 's/\r//g' /tmp/env.sh > build/env.sh
