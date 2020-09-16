#!/bin/bash

# create a file system protection file (first unencrypted)
scone fspf create /fspf/fspf-file/fs.fspf
# root region (i.e., "/") is not protected in this demo
scone fspf addr /fspf/fspf-file/fs.fspf / --not-protected --kernel /
# add encrypted region /fspf/encrypted-files
scone fspf addr /fspf/fspf-file/fs.fspf /fspf/encrypted-files/ --encrypted --kernel /fspf/encrypted-files/
# add all files in directory /fspf/native-files/ to /fspf/encrypted-files/
scone fspf addf /fspf/fspf-file/fs.fspf /fspf/encrypted-files/ /fspf/native-files/ /fspf/encrypted-files/
# authenticate glibc and related libs
scone fspf addr /fspf/fspf-file/fs.fspf /opt/scone/lib --authenticated --kernel /opt/scone/lib
scone fspf addf /fspf/fspf-file/fs.fspf /opt/scone/lib /opt/scone/lib
# authenticate python interpreter
scone fspf addr /fspf/fspf-file/fs.fspf /root/miniconda --authenticated --kernel /root/miniconda
scone fspf addf /fspf/fspf-file/fs.fspf /root/miniconda /root/miniconda
# finally, encrypt the file system protection file and store the keys in directory (we assume in this demo that wee run on a trusted host)
scone fspf encrypt /fspf/fspf-file/fs.fspf > /fspf/native-files/keytag
