## Confidential Minecraft

This fun example illustrates how simple it is to take an existing, **unmodified** container and deploy it onto Azure Container Instances (ACI) using the Confidential SKU and Customer Managed Key (CMK) configuration. This results in a container that is protected using encryption at-rest and in-use. In-transit encryption is provided by the application itself.

This will create a Minecraft Bedrock server on a confidential container using these artifacts based on this Github repo from Geoff Bourne "itzg" (https://github.com/itzg/docker-minecraft-bedrock-server)

For more information on Azure Confidential Compute see (https://aka.ms/accdocs)
This simplified example uses the default policy, but you can investigate more advanced policies here (https://github.com/Azure/azure-cli-extensions/blob/main/src/confcom/azext_confcom/README.md)

At the time of writing, Confidential Containers on ACI is a Public Preview feature (https://azure.microsoft.com/en-us/updates/public-preview-confidential-containers-on-aci/)

You will need..

- An Azure subscription, if you don’t have one already you can create a free trial at https://azure.microsoft.com/free/
- Azure CLI https://learn.microsoft.com/cli/azure or you can use Azure Cloud Shell https://learn.microsoft.com/azure/cloud-shell/overview
- A Minecraft client https://minecraft.net/get-minecraft clients are available for a variety of PC, Mac(1) and mobile platforms, free trials are available.

*(1)Note this example uses the Bedrock server which does not currently have a Mac client, if you want to try from a Mac you'll need the 'Java' server - see the Java docker container (https://github.com/itzg/docker-minecraft-server)*


*Note: substitute values in angle-brackets to suit your environment*

**Step 1:** Setup variables for the resource group and subscription

    demorg="<YOUR RESOURCE GROUP>"
    demosubsid="<YOUR SUBSCRIPTION ID>"

**Step 2:** Login to your Azure tenant and select the target subscription

    az login --tenant "<YOUR TENANT>.onmicrosoft.com"
    az account set --subscription $demosubsid
    
**Step 3:** Create a resource group to hold the Azure objects

    az group create -l northeurope -n $demorg #create the Resource Group

**Step 4:** Get the existing ACI Service Principal (1 per tenant, located using well known GUID)
    
    az ad sp show --id 6bb8e274-af5d-4df2-98a3-4fd78b4cafd9

**Step 5:** Edit the 1.MinecraftConfidential-CMKconfig.json file adjusting values in angle-brackets to suit your environment

Step 6: Run the 1. ARM template to create the Azure Key Vault (AKV) instance + 1 x encryption key for Customer Managed Key and note the output for use in subsequent steps
    
    az deployment group create --resource-group $demorg --template-file 1.MinecraftConfidential-CMKconfig.json  

**Step 7:** Give the ACI Service Principal access to the keyvault (so it can read the Customer Managed Key (CMK)) - the ID for the Service Principal is obtained by the az ad sp show command above !! ID will be different per tenant !!

    az keyvault set-policy --name "<YOUR KEYVAULT NAME>" --resource-group $demorg --object-id "<GUID OF YOUR ACI SP>" --key-permissions get unwrapKey

**Step 8:** Edit the 2.MinecraftConfidentialBedrockCMK.json file to suit your environment, using values from the output of the previous commands to enter parameters noted in angle brackets <VALUE>

**Step 9:** Finally, create an Azure Container Instance using Confidential Compute using the ARM template you've built.

    az deployment group create --resource-group $demorg --template-file 2.MinecraftConfidentialBedrockCMK.json

You can now connect to your minecraft server using a Minecraft client (get clients here https://www.minecraft.net/en-us/download) by adding a server using the FQDN of your container (e.g. YourDnsLabel.northeurope.azurecontainer.io)

![test gif!](HowToConnect.gif)
