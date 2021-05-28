#!/bin/bash
#
# Access to this file is granted under the SCONE SOURCE CODE LICENSE V1.0 
#
# Commercial use of any product using this file requires a commercial 
# license from scontain UG, www.scontain.com.
#
# also see https://sconedocs.github.io
#
# Copyright (C) 2018 Scontain UG

# For more details, see SCONE Fileshield: https://sconedocs.github.io/SCONE_Fileshield/

# Initialize /fspf/encrypted-files/
mkdir -p encrypted-files
rm -rf encrypted-files/*

# Encrypt files in /fspf/input and store in /fspf/encrypted-files/
scone fspf create encrypted-files/volume.fspf
scone fspf addr encrypted-files/volume.fspf / --not-protected --kernel /
scone fspf addr encrypted-files/volume.fspf /fspf/encrypted-files/ --encrypted --kernel /fspf/encrypted-files/
scone fspf addf encrypted-files/volume.fspf /fspf/encrypted-files/ /fspf/input/code /fspf/encrypted-files/ 
scone fspf encrypt encrypted-files/volume.fspf > keytag.txt

# This meta-data will be obtained from the CAS component (Configuration and Attestation Service)
# -------------------------------
# The SCONE CAS is a component of the SCONE infrastructure. 
# Programs executed in Enclaves connect to CAS to obtain their Confidential Configuration.
# CAS Provisions this configuration only after it has verified the integrity and authenticity of the requesting enclave.
# CAS also checks that the requesting enclave is allowed to obtain the confidential configuration.
# Initially, configurations are pushed to the CAS with the SCONE Client.

# Details:
# https://www.usenix.org/system/files/conference/osdi16/osdi16-arnautov.pdf
# https://sconedocs.github.io/cas_intro/
# https://sconedocs.github.io/hello_world_kubernetes/#run-with-remote-attestation
# https://sconedocs.github.io/hello_world_kubernetes/#tls-with-certificates-auto-generated-by-cas
export SCONE_FSPF_KEY=$(cat keytag.txt | awk '{print $11}')
export SCONE_FSPF_TAG=$(cat keytag.txt | awk '{print $9}')
export SCONE_FSPF=/fspf/encrypted-files/volume.fspf
