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
    .appName("process_places_details") \
    .getOrCreate()
    
places_detail = os.path.join(settings.path_data, 'data/ext/places_detail.pdf')

cols = ['turn', 'permission', 'place_name', 'place_code', 'date_entry', 
        'plenary_date', 'address', 'colony', 'cp', 'city', 'state']

data = []
pages = None
Logger.info('reading the number pages of the PDF')
with pdfplumber.open(places_detail) as pdf:
    pages = len(pdf.pages)
    Logger.info('the PDF contains {} pages'.format(pages))
    
for i in range(pages):
    Logger.info('reading page {}'.format(i))
    with pdfplumber.open(places_detail) as pdf:
        data_temp = pdf.pages[i].extract_table()
        if data_temp:
            data += [Row(**dict(zip(cols, x))) for x in data_temp]

Logger.info('Generating a dataframe of the places details table')
df = spark.createDataFrame(data)
df = df.filter(df.colony != 'Colonia')

Logger.info('selecting and casting columns of prices table')
df = df.select(
        ps_func.col('turn'),
        ps_func.col('permission'),
        ps_func.col('place_name'),
        ps_func.col('place_code'),
        ps_func.col('date_entry'),
        ps_func.col('plenary_date'),
        ps_func.col('address'),
        ps_func.col('colony'),
        ps_func.col('cp').cast(ps_types.IntegerType()).alias('cp'),
        ps_func.col('city'),
        ps_func.col('state')
)

path_name = os.path.join(settings.path_data, 'data/trans', 'places_details.parquet')
os.makedirs(os.path.join(settings.path_data, 'data/trans'), exist_ok=True)
if os.path.exists(path_name):
    shutil.rmtree(path_name)

Logger.info('writing the final file of the prices table')
df.write.parquet(path_name)