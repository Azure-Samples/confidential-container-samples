# Confidential Containers Samples

The term “confidential containers” refers to docker application (new or existing) containers packaged with additional components if necessary to run on the hardware that provides strong protections of Confidential Computing to improve the overall security posture of the container application and the data-in-use.

Confidential containers is about taking an existing docker container application and running it on a hardware based Trusted Execution Environment (enclave). This is the fastest path to container confidentiality including the container protection through encryption, thus enabling lift and shift with no/minimal changes to your business logic.

[Read more here](http://aka.ms/confidentialcontainers)

## Samples Collection Index

This repo is organized by folders that states the sample name followed by the enablers of confidential containers. A typical folder name follows this standard < samplename >-< enabername > :

* [Confidential HealthCare Demo With Scone, Confidential Inferencing & Azure Attestation](confidential-healthcare-scone-confinf-onnx/README.md) 

### Prerequisites

This implementation assumed the samples would be deployed into Azure Kubernetes Service (AKS) with Confidential Computing Nodes.

Please read more about Confidential Computing Nodes on AKS [here](https://aka.ms/acconakspreview).
