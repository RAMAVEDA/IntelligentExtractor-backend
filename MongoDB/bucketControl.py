from google.cloud import storage
import environ
import io
import os
import numpy as np
import datetime

env = environ.Env()

environ.Env.read_env()

client = storage.Client.from_service_account_json(
    json_credentials_path=env('API_KEYS'))

bucket = client.get_bucket('extractor_s1')


def gcupload_Excel(file):
    object_name_in_gcs_bucket = bucket.blob(
        '/Outputs_excel/'+str(datetime.datetime.now()).split()[0]+os.path.basename(file))
    object_name_in_gcs_bucket.upload_from_filename(file)


def gcdownload(from_path, to_path):

    object_name_in_gcs_bucket = bucket.blob(from_path)

    object_name_in_gcs_bucket.download_to_filename(to_path)


def gcdownload_str(path):
    object_name_in_gcs_bucket = bucket.blob(path)
    e = object_name_in_gcs_bucket.download_as_string()
    nparr = np.fromstring(e, np.uint8)
    return nparr

def gcdownload_byt(path):
    object_name_in_gcs_bucket = bucket.blob(path)
    e = object_name_in_gcs_bucket.download_as_bytes()
    return e

def gcupload(path, f):
    b = io.BytesIO()
    f.save(b, 'JPEG')
    f.close()
    object_name_in_gcs_bucket = bucket.blob(path)
    object_name_in_gcs_bucket.upload_from_string(
        b.getvalue(), content_type='image/jpeg')
