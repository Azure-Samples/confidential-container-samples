from azure.identity import ClientSecretCredential
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.identity_service import ConfidentialLedgerIdentityServiceClient
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger import (
    LedgerUserRole,
    TransactionState,
)
import sys
from pygtail import Pygtail

# Getting logs from file path (#TODO: integrate directly into ASP.NET web app)
logPath = "D:\ContosoHR_logs"

# Initiate Identity Service Client
identity_client = ConfidentialLedgerIdentityServiceClient("https://identity.accledger.azure.com/")

# Get NetworkIdentity Object for specific LedgerName
if identity_client is not None:

    # Create Token Credential Artifacts from command line arguments
    clientId = sys.argv[1]
    clientSecret = sys.argv[2]
    tenantId = sys.argv[3]

    # Localize ledger_id
    ledgerId = sys.argv[4]
    ledgerUrl = "https://%s.eastus.cloudapp.azure.com" % ledgerId

    network_identity = identity_client.get_ledger_identity(
        ledger_id=ledgerId
    )
    
    # Write network cert to file
    ledger_tls_cert_file_name = "ledger_certificate.pem"
    with open(ledger_tls_cert_file_name, "w") as cert_file:
        cert_file.write(network_identity.ledger_tls_certificate)
        print(network_identity.ledger_tls_certificate)
    
    # Create a Credential Object
    credentials = ClientSecretCredential(tenant_id=tenantId, client_id=clientId, client_secret=clientSecret)
    
    # Create LedgerClient object
    ledger_client = ConfidentialLedgerClient(ledgerUrl, credentials, ledger_tls_cert_file_name)

    while True:
        for line in Pygtail(logPath + "\\"+ "querylogs.txt"):
            
            # Append Entry to Ledger
            append_result = ledger_client.append_to_ledger(
                entry_contents=line, wait_for_commit=True
            )
            
            # Grab committed Transaction ID
            Trx_ID = append_result.transaction_id

            # FYI:
            # Since we're not generating/submitting logs rapidly here, Trx_ID will increment by 2. 
            # Flow: single business transaction + a single signature transaction
            # E.g. We POST an entry that gets 2.15, signature is emitted that gets 2.16
            # E.g. If we submit entries faster, we'll get contiguous transaction IDs - with signatures after.
            
            # The logic is:
            # The service produces periodic signatures so that we have after-the-fact audit/blame of the transaction history. 
            # The replica nodes in the chain validate the signatures as they receive them.
            # The signature is unique to each node, so if there are invalid transactions we can blame the node that produced them.

            # Read back and validate committed entry via Transaction ID
            entry = ledger_client.get_ledger_entry(transaction_id=Trx_ID)
            assert entry.contents == line
            print(Trx_ID + " | " + entry.contents)

else:
    print("Not a valid ledger")