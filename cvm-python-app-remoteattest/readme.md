# CVM Atteststion Web API Sample Details with MAA

This solution is to be deployed on a Azure Confidential VM's DCav5/Ecav5 will run a Python web Server that leverages a [CVM attestation client](https://github.com/Azure/confidential-computing-cvm-guest-attestation) and does the below
    1. Builds Linux Attestation application client
    1. Runs this Linux app as subprocess within Python file
        1. fetches raw SNP hardware report and sends that to MAA for verification
    1. Decodes the JWT from MAA and sends it back to web server

## Solution details

A Web GET request will print the MAA token after going through the attestation flow, Here is teh basic architecture

![CVM Attestation Web API](./images/CVMAttestationPythonWEBAPI.png "Overall app architecture")

A screenshot of webAPI GET request after successful attestation flow

![Web API FER Response](./images/webapiget.jpg "Overall app architecture")


## Sample Response from Web API

You can view a sample output of this WEB API GET method [here](outputjsonsample.json)

## Deployment Details

Build an image using Docker build
or run python application with "sudo python3 app.py"
Install Docker engine on CVM
Do Docker Run
Expose port 8081 from CVM

## Extension

This WEB API can be embedded in the overall application flow that brings in the attest and then exchange secrets or perform data computation.