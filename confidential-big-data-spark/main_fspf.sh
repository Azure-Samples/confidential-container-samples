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

scone fspf create /fspf.pb
scone fspf addr /fspf.pb / --not-protected --kernel /
scone fspf addr /fspf.pb /usr/lib --authenticated --kernel /usr/lib
scone fspf addf /fspf.pb /usr/lib /usr/lib
scone fspf addr /fspf.pb /lib --authenticated --kernel /lib
scone fspf addf /fspf.pb /lib /lib
scone fspf addr /fspf.pb /usr/local/lib/python3.8 --authenticated --kernel /usr/local/lib/python3.8
scone fspf addf /fspf.pb /usr/local/lib/python3.8 /usr/local/lib/python3.8
scone fspf addr /fspf.pb /spark/jars --authenticated --kernel /spark/jars
scone fspf addf /fspf.pb /spark/jars /spark/jars
scone fspf addr /fspf.pb /usr/lib/jvm/java-1.8-openjdk/jre/lib/amd64/server --authenticated --kernel /usr/lib/jvm/java-1.8-openjdk/jre/lib/amd64/server
scone fspf addf /fspf.pb /usr/lib/jvm/java-1.8-openjdk/jre/lib/amd64/server /usr/lib/jvm/java-1.8-openjdk/jre/lib/amd64/server 
scone fspf encrypt /fspf.pb > /out/main_fspf_keytag.txt
mv /fspf.pb /out
