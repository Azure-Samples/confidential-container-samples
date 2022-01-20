FROM registry.scontain.com:5050/clenimar/pyspark:5.6.0plus

USER root

# Copy libraries for runtime
ADD input/libraries/* /spark/jars/

ENV SCONE_HEAP=4G SCONE_FORK=0 SCONE_ALLOW_DLOPEN=1 SCONE_MPROTECT=1 SCONE_SYSLIBS=1 SCONE_LOG=ERROR

# libzstd-jni.so is extracted during execution from zstd-jni-1.4.8-1.jar into
# /tmp. dlopen fails because of that since /tmp is not a protected region. we
# resolve this by extracting the library beforehand into /usr/lib. same thing with liblz4
RUN scone-signer sign --env /usr/lib/jvm/java-1.8-openjdk/bin/java && \
    scone-signer sign --env --heap 1G --mprotect 0 /usr/local/bin/python3 && \
    rm /usr/local/bin/python3 && mv /usr/local/bin/python3.8 /usr/local/bin/python3 && \
    cd /tmp && unzip /spark/jars/zstd-jni-1.4.8-1.jar && cp linux/amd64/libzstd-jni.so /usr/lib && \
    rm -rf /tmp/* && \
    unzip /spark/jars/lz4-java-1.7.1.jar && cp net/jpountz/util/linux/amd64/liblz4-java.so /usr/lib && \
    rm -rf /tmp/*

ENTRYPOINT [ "/opt/entrypoint.sh" ]
