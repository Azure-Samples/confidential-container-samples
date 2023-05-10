**Simple Confidential AKS Worker Node Demo**

This demo will build out an AKS cluster, add confidential nodes using the DCasv5 SKU based on AMD SEV-SNP technology and then deploy some example containers, including a web-based attestation client which you can use to validate attestation claims about the AKS worker nodes.

Pre-requisites

- An Azure subscription, if you don’t have one already you can create a free trial at https://azure.microsoft.com/free/
- Azure CLI https://learn.microsoft.com/cli/azure or you can use Azure Cloud Shell https://learn.microsoft.com/azure/cloud-shell/overview
- Kubernetes CLI - install using the az aks command (https://learn.microsoft.com/en-us/cli/azure/aks?view=azure-cli-latest#az-aks-install-cli)
    - az aks install-cli
- The curl command line HTTP query tool Link if your platform does not have a default install (https://curl.se/download.html)
- JQ (https://stedolan.github.io/jq/download/) to make it easier to decode JSON responses on the command line
- Helm for installing some simple container packages (https://helm.sh/docs/intro/install/)
 
**STEP1**<p>
The demo uses several environment variables to simplify the build-out process as follows

    export pgrg="<RESOURCE GROUP NAME>"
    export subsid="<YOUR AZURE SUBSCRIPTION ID"
    export aksrg="<RESOURCE GROUP TO CONTAIN AKS CLUSTER>"
    export aksclustername="<AKS CLUSTER NAME, KEEP THIS SHORT>"
    export acrname="<AZURE CONTAINER REGISTRY NAME>"
    export accnodepoolname="<NAME FOR CONFIDENTIAL NODES, KEEP THIS SHORT>"
    export wpdemo="<NAME OF WORDPRESS HELM DEPLOYMENT>"

**STEP 2**<p>
Login to your Azure tenant & target your subscription

    az login --tenant <TENANT NAME>.onmicrosoft.com
    az account set --subscription $subsid

**STEP 3**<p>
Create a resource group to hold resources

    az group create -l eastus -n $aksrg #create the RG

**STEP 4**<p>
Create an Azure Container Registry (ACR) to hold container images for your AKS cluster
    
    az acr create --resource-group $aksrg --name $acrname --sku Basic

**STEP 5**<p>
This set of commands will create an AKS cluster with a single general-purpose compute node and connect it to your ACR then it will add credentials to your local system to allow the usage of kubectl commands
    az aks create --resource-group $aksrg --name $aksclustername --node-count 1 --generate-ssh-keys --attach-acr $acrname
    az aks get-credentials --resource-group $aksrg --name $aksclustername

**STEP 6**<p>
Validate you have a working AKS setup
    
    kubectl get nodes

**STEP 7**<p>
The following command will add 3 nodes using the Standard_DCas_v5 SKU which are nodes using the AMD SEV-SNP technologies to support a Trusted Execution Environment (TEE) for Confidential Compute, all memory contents will be encrypted and the nodes execute inside the TEE

    az aks nodepool add --resource-group $aksrg --cluster-name $aksclustername --name $accnodepoolname --node-count 3 --node-vm-size Standard_DC4as_v5

Once the command has completed, you can use the following command to validate that the correct SKU is being used

    az aks nodepool show --resource-group $aksrg --cluster-name $aksclustername --name $accnodepoolname --query 'vmSize'

Now, you have a working AKS cluster with Confidential Worker nodes, it's time to validate it.

**STEP 8**<p>

Paste the following commands into a terminal to build the container and store it in your ACR instance (note: for Windows machines you'll need to adjust the '/' in paths to be '\' to match Windows conventions)

    git clone https://github.com/Azure-Samples/confidential-container-samples.git  
    cd ./confidential-container-samples/cvm-python-app-remoteattest/
    az acr build --registry $acrname --image cvmattest:v1 .
    kubectl apply -f "k8sdeploy.yaml" --validate=false 
    kubectl get svc azure-cvm-attest -w

Once the azure-cvm-attest service has a public IP address you can make an HTTP call to it, and pass the JSON formatted text it returns to JQ to make it easier to read

    curl http://<EXTERNAL_IP>:8081 | jq

**STEP 9**<p>

Install some simple community-contributed containers using Helm Charts, Helm (https://helm.sh) is a handy tool for quickly deploying simple containers
Note, these containers did not need to be modified in any way to make them benefit from Confidential Compute protections because you are deploying on to AKS Confidential Worker nodes the containers are transparently protected whilst they are in-use using a Trusted Execution Environment.

Add a Helm repo

    helm repo add azure-marketplace https://marketplace.azurecr.io/helm/v1/repo   

Deploy Wordpress

    helm install $wpdemo azure-marketplace/wordpress

If you wait a couple of minutes you'll be able to access the default Wordpress site for the container you just deployed using the IP address shown on the terminal.

Use the following command to discover some other Helm charts to deploy

   helm search repo -l azure-marketplace

