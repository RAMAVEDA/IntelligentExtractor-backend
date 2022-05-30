from datetime import datetime, timedelta
from azure.storage.blob import (
    generate_blob_sas,
    BlobSasPermissions
)
import environ

env = environ.Env()

environ.Env.read_env()

azure_account_name = env("AccountName")
azure_primary_key = env("AccountKey")
azure_container = env("BUCKET")

def generate_signed_url(azure_blob):
    sas_blob = generate_blob_sas(account_name= azure_account_name, 
                            container_name= azure_container,
                            blob_name= azure_blob,
                            account_key= azure_primary_key,
                            #For writing back to the Azure Blob set write and create to True 
                            permission=BlobSasPermissions(read=True, write= False, create= False),
                            #This URL will be valid for 1 hour
                            expiry=datetime.utcnow() + timedelta(hours=1))
    url = 'https://'+azure_account_name+'.blob.core.windows.net/'+ azure_container +'/'+ azure_blob +'?'+ sas_blob

    print("Generated GET signed URL:")
    print(url)
    return url

