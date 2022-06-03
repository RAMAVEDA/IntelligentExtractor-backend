from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
import environ
import os
import datetime

env = environ.Env()

environ.Env.read_env()

containerName = env("BUCKET")
connect_str = env("connect_str")
blob_service_client = BlobServiceClient.from_connection_string(connect_str)


def upload_Excel(file,data):
    blob_client = blob_service_client.get_blob_client(container=containerName, blob='Outputs_excel/'+str(datetime.datetime.now()).split()[0]+'/'+os.path.basename(file))
    blob_client.upload_blob(data)


def download(from_path, to_path):
    blob_client = blob_service_client.get_blob_client(container=containerName, blob=from_path)
    with open(to_path, "wb") as my_blob:
        download_stream = blob_client.download_blob()
        my_blob.write(download_stream.readall())

def download_byt(path):
    blob_client = blob_service_client.get_blob_client(container=containerName, blob=path)
    download_stream = blob_client.download_blob()
    e = (download_stream.readall())
    return e

def msupload(path, f):
    print('upload',containerName,path)
    blob_client = blob_service_client.get_blob_client(container=containerName, blob=path)
    blob_client.upload_blob(f)
    