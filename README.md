---
page_type: sample
languages:
- yaml
- python
- shell
- C++
products:
- azure-confidential-computing
- azure-kubernetes-service
- azure attestation-service
- confidential-containers
description: "Confidential containers on AKS samples"
urlFragment: confidential-containers-samples
---

# Confidential container samples

![Flask sample MIT license badge](https://img.shields.io/badge/license-MIT-green.svg)

Confidential containers are a set of capabilities that allow standard containers (Linux or Windows) to run in a hardware root of trusted established environment. Confidential containers refer to a set of capabilities that achieves the principles of confidential computing. [Read more about confidential containers here](http://aka.ms/confidentialcontainers)

**Important:** This repo is aggregated samples based on real world customer scenarios based and may involve Azure Partner Solution or an Open Source Project for its implementation. All implementations in this repo will host Azure Kubernetes Service (AKS) based deployments. Please review the sample repo for pre-requisites to deploy and run this application.

## Prerequisites

- [GitHub account](https://github.com/join)
- [Azure subscription](https://azure.microsoft.com/free/)

## How to use this template repository

This repo is organized by folders that states the sample name followed by the enablers of confidential containers. A typical folder name follows this standard < samplename >-< enabername > :

### Confidential Healthcare Application on Intel SGX based confidential containers

[Confidential HealthCare Implementation with Scone, Confidential Inferencing & Azure Attestation](confidential-healthcare-scone-confinf-onnx/README.md)

### Confidential Big Data Analytics with Apache Spark and Azure SQL Always Encrypted secured enclaves on Intel SGX based confidential containers

[Confidential Big Data Analytics with Apache Spark on SGX-enabled Containers using Scone](confidential-big-data-spark/README.md)

### Apache Spark applications with BigDL PPML and Occlum on Azure Intel SGX enabled Confidential Virtual machines on AKS

[Apache Spark sample with NY Taxi data sample data processing from with containers using open source software Occlum](confidential-bigdl-spark/README.md)

### Remote attestation Web API Helper for Confidential VM's (AMD SEV-SNP) on AKS

[Confidential VM (AMD SEV-SNP) Remote Attestation Web API Helper Sample](cvm-python-app-remoteattest/readme.md)

### Confidential Azure Container Instances ( ACI )  demo with remote attestation

[Confidential ACI demo](confidential-aci-demo/readme.md)

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit <https://cla.opensource.microsoft.com.>

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
