import os

import shutil
from config.conf import AppSettings
from scr.utils.extractor import data_extractor
from pyspark.sql import SparkSession, Row, types as ps_types, functions as ps_func
from pyspark.sql.types import FloatType, IntegerType
import pdfplumber
import logging

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


path_name = os.path.join(settings.path_data, 'data/trans', 'prices.parquet')
os.makedirs(os.path.join(settings.path_data, 'data/trans'), exist_ok=True)
if os.path.exists(path_name):
    shutil.rmtree(path_name)

Logger.info('writing the final file of the prices table')
df.write.parquet(path_name)