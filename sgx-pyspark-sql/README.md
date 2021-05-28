# Confidential Analytics with Apache Spark on SGX-enabled Containers

## Overview

This repository demonstrates the following architecture for **Confidential Analytics** on Azure SGX enabled machines (**AKS** or **Standalone**) for running containerized applications: <br>

> 💡 Confidential analytics in this context is meant to imply: **_"run analytics on PII data with peace of mind against data exfiltration"_** - this includes potential `root`-level access breach both internally (rogue admin) or externally (system compromise).

![Architecture Diagram](images/Architecture-Diagram.png)

### Goal

Demonstrate how to run **end-to-end Confidential Analytics** on Azure (presumably on PII data), leveraging [Azure SQL Always Encrypted with Secure Enclaves](https://docs.microsoft.com/en-us/sql/relational-databases/security/encryption/always-encrypted-enclaves?view=sql-server-ver15) as the database, and containerized **Apache Spark** on SGX-enabled Azure machines for analytics workloads.

## Live Demo

[![SCONE: Secure Linux Containers with Intel SGX](https://img.youtube.com/vi/em6ovuznAf8/0.jpg)](https://youtu.be/em6ovuznAf8)

### Key points

- **Azure DC Series**: We run a containerized [Spark 3.1.1](https://spark.apache.org/releases/spark-release-3-1-1.html) application, on an [**Azure DC4s_v2**](https://docs.microsoft.com/en-us/azure/virtual-machines/dcv2-series) machine running Docker. These machines are backed by the latest generation of Intel XEON E-2288G Processor with [SGX extensions](https://software.intel.com/content/www/us/en/develop/topics/software-guard-extensions.html) - the **_key component_** to enabling the core message of this demo.
  - **💡 Note**: This demo works identically well on [AKS running DC4s_v2 nodes](https://docs.microsoft.com/en-us/azure/confidential-computing/confidential-computing-enclaves). We perform the demo on the standalone node to enjoy the additional benefits of RDP for demonstrations purposes that `kubectl` wouldn't allow as easily.
- **SCONE**: To run Spark inside an SGX enclave - we leverage [SCONE](https://docs.microsoft.com/en-us/azure/confidential-computing/confidential-containers#scone-scontain), who have essentially taken the [Open Source Spark code](https://sconedocs.github.io/sconeapps_spark/), and wrapped it with their runtime so that Spark can run inside SGX enclaves (a task that requires deep knowledge of the SGX ecosystem - something SCONE is an expert at).

  - **Introduction**: Here's a fantastic video on SCONE from one of the founders - [Professor Christof Fetzer](https://github.com/christoffetzer): <br>
    [![Scone walkthrough](https://img.youtube.com/vi/aoA8pwasMqs/0.jpg)](https://youtu.be/aoA8pwasMqs)
  - **Deep dive**: If you're looking for deeper material on SCONE, here's an academic paper describing the underlying mechanics: [link](https://www.usenix.org/system/files/conference/osdi16/osdi16-arnautov.pdf)
  - **Deep dive w/ commentary**: This is an entertaining walkthrough of the above paper by [Jessie Frazelle](https://github.com/jessfraz) - also a leader in the Confidential Computing space. <br>
    [![SCONE: Secure Linux Containers with Intel SGX](https://img.youtube.com/vi/3UYczEYrxuY/0.jpg)](https://youtu.be/3UYczEYrxuY)

  - **Sconedocs**: Scone's official documentation for getting started: [link](https://sconedocs.github.io/)

### Pre-requisites

1. Registry for access to the 2 Spark images used per scenario:

   - **Scenario 1**: `registry.scontain.com:5050/sconecuratedimages/www2019:sgx-pyspark`
   - **Scenario 2**: `registry.scontain.com:5050/lequocdo/sgx-pyspark/spark3.1.1-scone5.3.0`

   For access to these images - follow the steps [here](https://sconedocs.github.io/SCONE_Curated_Images). If you have any questions/access issues, please reach out to [SCONE](info@scontain.com) with your Gitlab ID and the images you're trying to access - they'll promptly resolve it.

2. Follow the tutorial here to deploy an Azure SQL Always Encrypted with Secure Enclaves Database with some sample PII data: [link](https://docs.microsoft.com/en-us/azure/azure-sql/database/always-encrypted-enclaves-getting-started) 3. A **DC4s_v2** VM deployment (standalone or in AKS cluster)

- **Scenario 1** (baseline) can run on any machine with an Intel CPU (including the DC4s_v2 machine). In the demo, we use a Surface laptop 3 with Docker Desktop.
- **Scenario 2** will not work without SGX - i.e. must run on an Azure DC series machine. You can enable [xfce](https://www.xfce.org/) to get an RDP interface.

## Scenario 1: Spark job running on non-SGX hardware

![Scenario 1](images/Scenario-1.png)

**Setup**

1. RDP into VM/laptop
2. Navigate to `http://localhost:28778/` [(log.io)](https://github.com/NarrativeScience/log.io) and `localhost:8080/` [(Spark Web UI)](https://spark.apache.org/docs/3.0.0-preview/web-ui.html)

**Execute steps**

```bash
# Run Container
docker run -it --rm --name "sgx_pyspark_sql" --privileged -p 8080:8080 -p 6868:6868 -p 28778:28778 aiaacireg.azurecr.io/scone/sgx-pyspark-sql sh

# Explore Docker Entrypoint to see startup
vi /usr/local/bin/docker-entrypoint.sh

# Replace the JDBC endpoint before running job
vi input/code/azure-sql.py

# E.g. jdbc:sqlserver://your--server--name.database.windows.net:1433;database=ContosoHR;user=your--username@your--server--name;password=your--password;

# Scenario 1: Scone: Off | Data: Encrypted | Code: Plaintext
############################################################
# Run Spark job
/spark/bin/spark-submit --driver-class-path input/libraries/mssql-jdbc-9.2.1.jre8.jar input/code/azure-sql.py >> output.txt 2>&1 &

# Testing the memory attack
./memory-dump.sh

```

## Scenario 2: Spark with Scone running on SGX (DC4s_v2)

![Scenario 2](images/Scenario-2.png)

**Setup**

1. RDP into Azure DC VM (need xfce or similar desktop interface)
2. Navigate to `http://localhost:6688/#{%221618872518526%22:[%22spark|SCONE-PySpark%22]}` [(log.io - newer version)](https://github.com/NarrativeScience/log.io) and `localhost:8080/` [(Spark Web UI)](https://spark.apache.org/docs/3.0.0-preview/web-ui.html)

**Execute steps**

```bash
# Elevate to superuser for Docker
sudo su -

# Set SGX variable - for more information, see https://sconedocs.github.io/sgxinstall/
export MOUNT_SGXDEVICE="-v /dev/sgx/:/dev/sgx"

# Run Container
docker run $MOUNT_SGXDEVICE -it --rm --name "sgx_pyspark_3" --privileged -p 8080:8080 -p 6688:6688 aiaacireg.azurecr.io/scone/sgx-pyspark-3 sh

# Explore Docker Entrypoint to see startup
vi /usr/local/bin/docker-entrypoint.sh

# Replace the JDBC endpoint before running job
vi input/code/azure-sql.py

# E.g. jdbc:sqlserver://your--server--name.database.windows.net:1433;database=ContosoHR;user=your--username@your--server--name;password=your--password;columnEncryptionSetting=enabled;enclaveAttestationUrl=https://your--attestation--url.eus.attest.azure.net/attest/SgxEnclave;enclaveAttestationProtocol=AAS;keyVaultProviderClientId=your--sp--id;keyVaultProviderClientKey=your--sp--secret;

# Scenario 1: Scone: On | Data: CMK Protected | Code: Plaintext
###############################################################
# Run Spark job
/spark/bin/spark-submit --driver-class-path input/libraries/mssql-jdbc-9.2.0.jre8-shaded.jar input/code/azure-sql.py >> output.txt 2>&1 &

# Testing the memory attack
./memory-dump.sh

# Scenario 2: Scone: On | Data: CMK Protected | Code: Encrypted
###############################################################
# Show that there is no encrypted code
tree

# Encrypt code into fspf
source ./fspf.sh

# Show the encrypted code
tree
vi encrypted-files/azure-sql.py

# Run Spark job
/spark/bin/spark-submit --driver-class-path input/libraries/mssql-jdbc-9.2.0.jre8-shaded.jar encrypted-files/azure-sql.py >> output.txt 2>&1 &

# Testing the memory attack
./memory-dump.sh
```
