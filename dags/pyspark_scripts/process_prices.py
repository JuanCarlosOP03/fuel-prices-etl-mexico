import os

import shutil
from config.conf import AppSettings
from scr.utils.extractor import data_extractor
from pyspark.sql import SparkSession, Row, types as ps_types, functions as ps_func
from pyspark.sql.types import FloatType, IntegerType
import pdfplumber
import logging
import datetime as dt

Logger = logging.getLogger(__name__)
settings = AppSettings()

Logger.info('starting session in spark')
spark = SparkSession.builder \
    .appName("process_prices") \
    .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.15.0") \
    .getOrCreate()

file_prices = os.path.join(settings.path_data, 'data/ext/prices.xml')

Logger.info('reading xml of prices')
df = spark.read.format("xml") \
    .option("rowTag", "place") \
    .option("encoding", "utf-8")\
    .load(file_prices)
    
Logger.info('exploding the gas_price column')
df = df.withColumn("gas_price", ps_func.explode("gas_price"))

Logger.info('selecting and casting columns of prices table')
df = df.select(
    ps_func.col("_place_id").cast(IntegerType()).alias("place_id"),
    ps_func.col("gas_price._VALUE").cast(FloatType()).alias("price"),
    ps_func.col("gas_price._type").alias("type_product")
)
df = df.withColumn("fuel_type", ps_func.when(df.type_product == 'diesel', 'diesel').otherwise('gasolina'))

Logger.info('writing the final file of the prices table')

conf_s3 = settings.conf_s3

spark._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
spark._jsc.hadoopConfiguration().set("fs.s3a.region", conf_s3.get('AWS_REGION'))
spark._jsc.hadoopConfiguration().set("fs.s3a.endpoint", conf_s3.get('AWS_S3_ENDPOINT'))
spark._jsc.hadoopConfiguration().set("fs.s3a.access.key", conf_s3.get('AWS_ACCESS_KEY_ID'))
spark._jsc.hadoopConfiguration().set("fs.s3a.secret.key", conf_s3.get('AWS_SECRET_ACCESS_KEY'))
spark._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

df.write \
    .format("parquet") \
    .mode("overwrite")\
    .save(f"s3a://{conf_s3.get('AWS_S3_BUCKET')}/data/fuel_data/{dt.date.today().strftime('%Y%m%d')}/prices.parquet")