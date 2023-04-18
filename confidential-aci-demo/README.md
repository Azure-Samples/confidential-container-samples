# Confidential containers on Azure Containers Instances demo 

## Overview 

The confidential containers on Azure Containers Instances walks you through the following scenarios using a jupyter notebook.  

* Build a container image and deploy a container group to Azure Container Instances which runs in a trusted execution environment (TEE) with a verifiable security policy 
* Request a remote attestation from the deployed container group. 
* Simulate an error scenario where we fail to launch a container group by changing the container image. 
* Deploy a container group with the updated container image and show how this is reflected in the remote attestation. 
  
## Setup and prerequisites 

The demo requires the following to be available on your machine.

* Jupyter notebook : https://jupyter.org/install
* Azure CLI : https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
* Confcom extension for CLI : https://learn.microsoft.com/en-us/cli/azure/confcom?view=azure-cli-latest 
* docker desktop : https://www.docker.com/products/docker-desktop/

Please also make sure that you are signed into Azure CLI and select the subscription that you want to use. Azure CLI is a command-line tool that allows you to manage your Azure resources and services. You can sign in to Azure CLI by using the `az login` command and follow the instructions. To select the subscription that you want to deploy in, you can use the `az account set --subscription <subscription-id>` command. You can find your subscription ID by using the `az account list` command. This step is important to avoid deploying the resources in the wrong subscription or avoid errors while using the jupyter notebook. 