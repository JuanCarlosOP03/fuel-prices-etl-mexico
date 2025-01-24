from scr.config.conf import AppSettings
import logging
import requests
import os

Logger = logging.getLogger(__name__)

def data_extractor(url: str, filebasename, **kwargs):
    settings = AppSettings()
    
    Logger.info('starting process of download at the ulr: {}'.format(url))
    response = requests.get(url, **kwargs)
    
    Logger.info('validating url response')
    if response.status_code != 200:
        Logger.info('error in request response')
        response.raise_for_status()
        
    data = response.content
    print(settings.path_data)
    
    file_path = os.path.join(settings.path_data, 'data/ext', filebasename)
    os.makedirs(os.path.join(settings.path_data, 'data/ext'), exist_ok=True)

    Logger.info('writing the result of the request')
    with open(file_path, 'wb') as f:
        f.write(data)
        
    Logger.info(f'The Files it has been saved in {file_path}')
    return file_path