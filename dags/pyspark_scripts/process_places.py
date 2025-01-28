import os

import shutil
from config.conf import AppSettings
from scr.utils.extractor import data_extractor
from pyspark.sql import SparkSession, Row, types as ps_types, functions as ps_func
from pyspark.sql.types import FloatType, IntegerType
import pdfplumber
import logging
import datetime as dt
import json

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

Logger.info('writing the final file of the places table')

conf_s3 = settings.conf_s3

spark._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
spark._jsc.hadoopConfiguration().set("fs.s3a.region", conf_s3.get('AWS_REGION'))
spark._jsc.hadoopConfiguration().set("fs.s3a.endpoint", conf_s3.get('AWS_S3_ENDPOINT'))
spark._jsc.hadoopConfiguration().set("fs.s3a.access.key", conf_s3.get('AWS_ACCESS_KEY_ID'))
spark._jsc.hadoopConfiguration().set("fs.s3a.secret.key", conf_s3.get('AWS_SECRET_ACCESS_KEY'))
spark._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

path = f"s3a://{conf_s3.get('AWS_S3_BUCKET')}/data/fuel_data/places.parquet"
df.write \
    .format("parquet") \
    .mode("overwrite")\
    .save(f"s3a://{conf_s3.get('AWS_S3_BUCKET')}/data/fuel_data/places.parquet")
    
