from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
from scr.utils.extractor import data_extractor
from scr.config.conf import AppSettings
from airflow.utils.dates import days_ago
from airflow.datasets import Dataset


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

settings = AppSettings()

def ingest_data_function(url: str, filebasename, ti, verify: str = None):
    path = data_extractor(url, filebasename, verify=verify)
    ti.xcom_push(filebasename, path)
    
jars_execute = ""\
     "/opt/spark/custom-jars/aws-java-sdk-bundle-1.12.262.jar,"\
     "/opt/spark/custom-jars/aws-java-sdk-core-1.12.262.jar,"\
     "/opt/spark/custom-jars/hadoop-aws-3.3.4.jar"


with DAG('Prices_Fuel', default_args=default_args, max_active_tasks=1) as dag:

    start_task = DummyOperator(
        task_id='start',
        dag=dag
    )
    
    task_ingest_prices_xml = PythonOperator(
        task_id='task_ingest_prices_xml',
        python_callable=ingest_data_function,
        op_kwargs={
            'url': settings.base_url.format('prices'), 
            'filebasename': 'prices.xml'
        },
        dag=dag
    )

    task_ingest_places_xml = PythonOperator(
        task_id='task_ingest_places_xml',
        python_callable=ingest_data_function,
        op_kwargs={
            'url': settings.base_url.format('places'), 
            'filebasename': 'places.xml'
        },
        dag=dag
    )

    task_ingest_places_detail_pdf = PythonOperator(
        task_id='task_ingest_places_detail_xml',
        python_callable=ingest_data_function,
        op_kwargs={
            'url': settings.url_place_details, 
            'filebasename': 'places_detail.pdf',
            'verify': False
        },
        dag=dag
    )

    task_process_prices_xml = SparkSubmitOperator(
        task_id='spark_process_prices',
        conn_id='spark_default',
        application='/opt/airflow/dags/pyspark_scripts/process_prices.py',
        total_executor_cores=2,
        executor_memory='512m',
        driver_memory='512m',
        packages='com.databricks:spark-xml_2.12:0.14.0',
        jars=jars_execute,
        dag=dag
    )

    task_upload_prices_s3_to_redshift = S3ToRedshiftOperator(
        task_id='task_upload_prices_s3_to_redshift',
        schema='mx_prices_fuel',
        table='prices',
        s3_bucket=settings.conf_s3.get('AWS_S3_BUCKET'),
        s3_key=f"s3://{settings.conf_s3.get('AWS_S3_BUCKET')}/data/fuel_data/prices.parquet",
        copy_options=['FORMAT AS PARQUET'],
        aws_conn_id='aws_default',
        redshift_conn_id='redshift_default',
        method='REPLACE',
        dag=dag,
    )
        
    task_process_places_xml = SparkSubmitOperator(
        task_id='spark_process_places',
        conn_id='spark_default',
        application='/opt/airflow/dags/pyspark_scripts/process_places.py',
        total_executor_cores=2,
        executor_memory='512m',
        driver_memory='512m',
        packages='com.databricks:spark-xml_2.12:0.14.0',
        jars=jars_execute,
        dag=dag
    )

    task_upload_places_s3_to_redshift = S3ToRedshiftOperator(
        task_id='task_upload_places_s3_to_redshift',
        schema='mx_prices_fuel',
        table='places',
        s3_bucket=settings.conf_s3.get('AWS_S3_BUCKET'),
        s3_key=f"s3://{settings.conf_s3.get('AWS_S3_BUCKET')}/data/fuel_data/places.parquet",
        copy_options=['FORMAT AS PARQUET'],
        aws_conn_id='aws_default',
        redshift_conn_id='redshift_default',
        method='REPLACE',
        dag=dag,
    )
    
    task_process_places_detail_pdf = SparkSubmitOperator(
        task_id='spark_process_places_details',
        conn_id='spark_default',
        application='/opt/airflow/dags/pyspark_scripts/process_places_details.py',
        total_executor_cores=2,
        executor_memory='512m',
        driver_memory='512m',
        jars=jars_execute,
        dag=dag
    )
    
    task_upload_places_details_s3_to_redshift = S3ToRedshiftOperator(
        task_id='task_upload_places_details_s3_to_redshift',
        schema='mx_prices_fuel',
        table='places_details',
        s3_bucket=settings.conf_s3.get('AWS_S3_BUCKET'),
        s3_key=f"s3://{settings.conf_s3.get('AWS_S3_BUCKET')}/data/fuel_data/places_details.parquet",
        copy_options=['FORMAT AS PARQUET'],
        aws_conn_id='aws_default',
        redshift_conn_id='redshift_default',
        method='REPLACE',
        dag=dag,
    )



    start_task >> [task_ingest_prices_xml, task_ingest_places_xml, task_ingest_places_detail_pdf]
    
    task_ingest_prices_xml >> task_process_prices_xml >> task_upload_prices_s3_to_redshift
    task_ingest_places_xml >> task_process_places_xml >> task_upload_places_s3_to_redshift
    task_ingest_places_detail_pdf >> task_process_places_detail_pdf >> task_upload_places_details_s3_to_redshift
    
    
