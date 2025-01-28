import os
from airflow.configuration import conf
from dotenv import load_dotenv

class AppSettings(object):
    def __init__(self) -> None:
        load_dotenv(
            dotenv_path='/opt/airflow/config/airflow.env'
        )

    @property
    def project_path(self):
        return os.path.join(conf.get("core", "dags_folder"), 'project_content')
    
    @property
    def path_data(self):
        return os.path.join(os.getenv('SPARK_PATH', 'N/A'), 'data')

    @property
    def base_url(self):
        return os.getenv('__BASE_URL', 'N/A')
    
    @property
    def url_place_details(self):
        return os.getenv('__URL_PLACE_DETAIL', 'N/A')
    
    @property
    def conf_s3(self):
        return {
            'AWS_S3_BUCKET': 'bi-services',
            'AWS_REGION': os.getenv('AWS_REGION', 'N/A'),
            'AWS_S3_ENDPOINT': os.getenv('AWS_S3_ENDPOINT', 'N/A'),
            'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID', 'N/A'),
            'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY', 'N/A'),
        }
    

if __name__ == '__main__':
    s = AppSettings()
    print(s.base_url)
    
    