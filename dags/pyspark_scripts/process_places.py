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
    .appName("process_places") \
    .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.15.0") \
    .getOrCreate()

file_places = os.path.join(settings.path_data, 'data/ext/places.xml')

Logger.info('reading xml of places')
df = spark.read.format("xml") \
    .option("rowTag", "place") \
    .option("encoding", "utf-8")\
    .load(file_places)

Logger.info('selecting and casting columns of prices table')
df = df.select(
    ps_func.col("_place_id").cast(IntegerType()).alias("place_id"),
    ps_func.col("cre_id"),
    ps_func.col("location.x").cast(FloatType()).alias("longitude"),
    ps_func.col("location.y").cast(FloatType()).alias("latitude"),
    ps_func.col("name").alias("place_name")
)

path_name = os.path.join(settings.path_data, 'data/trans', 'places.parquet')
os.makedirs(os.path.join(settings.path_data, 'data/trans'), exist_ok=True)
if os.path.exists(path_name):
    shutil.rmtree(path_name)
    
Logger.info('writing the final file of the prices table')
df.write.parquet(path_name)