# CVM Attestation Web API Sample Details with MAA

This solution is to be deployed on a [Azure Confidential VM's DCav5/Ecav5](https://docs.microsoft.com/en-us/azure/confidential-computing/confidential-vm-overview) and will run a Python web Server that leverages a [CVM attestation client](https://github.com/Azure/confidential-computing-cvm-guest-attestation) to do the below:

* Builds Linux Attestation application client
* Runs this Linux app as subprocess within Python file
* Fetches raw SNP hardware report and sends that to MAA for verification
* Decodes the JWT from MAA and sends it back to web server

## Scenario

This solution helps a client (any application/service) connecting with an application running in a CVM to go through verifying the trustworthiness of a platform and integrity of the binaries running inside it. [Microsoft Azure Attestation (MAA)](https://docs.microsoft.com/en-us/azure/attestation/overview) is used as verify of a Confidential VM instance. Once attested client apps can share secrets or sensitive data with the server app running in a CVM. 

## Solution details

A Web GET request will print the MAA token after going through the attestation flow running in a Confidential VM, Here is the basic architecture

![CVM Attestation Web API](./images/CVMAttestationPythonWEBAPI.png "Overall app architecture")

A screenshot of webAPI GET request after successful attestation flow

![Web API FER Response](./images/webapiget.jpg "Overall app architecture")

## Sample Response from Web API

You can view a sample output of this WEB API GET method [here](outputjsonsample.json)

## Deployment Details

Build an image using Docker build or run python application with "sudo python3 app.py"
Install Docker engine on CVM
Do Docker Run
Expose port 8081 from CVM

## Extension

This WEB API can be embedded in the overall application flow that brings in the attest and then exchange secrets or perform data computation.