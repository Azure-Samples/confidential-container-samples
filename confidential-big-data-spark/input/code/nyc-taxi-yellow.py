from __future__ import print_function

import sys, time
from operator import add
import os

from pyspark.sql import SparkSession

if __name__ == "__main__":
    print("###########################################")
    print("######### Starting Spark Session ##########")
    print("###########################################")
    # Start SparkSession
    spark = SparkSession \
            .builder \
            .appName("Confidential Spark Demo") \
            .getOrCreate()

    # Secrets - this information is retrieved from the
    # container env variables - which is populated by Scone CAS after we make sure
    # our Python interpreter and PySpark code were not tampered with.
    blob_account_name = os.environ.get("AZURE_BLOB_ACCOUNT_NAME", "")
    blob_container_name = os.environ.get("AZURE_BLOB_CONTAINER_NAME", "")
    blob_relative_path = os.environ.get("AZURE_BLOB_RELATIVE_PATH", "")
    blob_sas_token = r"%s" % os.environ.get("AZURE_BLOB_SAS_TOKEN", "")
    azure_sql_ae_jdbc = r"%s" % os.environ.get("AZURE_SQL_AE_JDBC", "")
    
    # Read from Azure Blob Storage
    wasbs_path = 'wasbs://%s@%s.blob.core.windows.net/%s' % (blob_container_name, blob_account_name, blob_relative_path)
    spark.conf.set(
      'fs.azure.sas.%s.%s.blob.core.windows.net' % (blob_container_name, blob_account_name),
      blob_sas_token)
    print('Remote blob path: ' + wasbs_path)
    input_df = spark.read.parquet(wasbs_path)
    
    print("###########################################")
    print("############### COUNT * ###################")
    print("###########################################")
    start_time = time.time() # Timer start
    print("\nInput DataFrame Count:", input_df.count())
    print("\nAggregation duration: ", time.time()-start_time) # Timer end

    print("###########################################")
    print("####### Azure SQL Always Encrypted ########")
    print("###########################################")
    # Loading Dataframe from Azure SQL
    AzureSQL_DF = spark.read \
        .format("jdbc") \
        .option("url", azure_sql_ae_jdbc) \
        .option("dbtable", "dbo.Employees") \
        .load()

    # Encrypted DataFrame is available in plaintext
    AzureSQL_DF.limit(10) \
               .show()

    # Can perform analytics as necessary
    # ....

    # Stop Spark Session
    spark.stop()