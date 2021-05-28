from __future__ import print_function

import sys, time
from operator import add
import os

from pyspark.sql import SparkSession

if __name__ == "__main__":
    # Generate delay to allow window for memory attack
    print("###########################################")
    print("######### Starting Spark Session ##########")
    print("###########################################")

    # Start SparkSession
    spark = SparkSession \
        .builder \
        .appName("Azure SQL application") \
        .getOrCreate()

    # Loading Dataframe from Azure SQL
    AzureSQL_DF = spark.read \
        .format("jdbc") \
        .option("url", "jdbc:sqlserver:...") \
        .option("dbtable", "dbo.Employees") \
        .load()

    AzureSQL_DF.limit(10) \
                 .show()

    spark.stop()

    # Generate delay to allow window for memory attack
    print("###########################################")
    print("#### Generate window for Memory Attack ####")
    print("###########################################")
    print("################ SLEEP 10 #################")
    print("###########################################")
    time.sleep(10)