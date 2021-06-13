from google.cloud import vision
import os
import environ

env = environ.Env()

environ.Env.read_env()

# client = storage.Client.from_service_account_json(
#     json_credentials_path=env(''))

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=env('API_KEYS') 

client = vision.ImageAnnotatorClient()
# vision.Image(vision.ImageSource(image_uri=image_paths[0]))
def consumeVision(image_paths):
    # image_paths = f"gs://" + env('BUCKET') +'//'
    # blob_source = vision.Image(source=vision.ImageSource(image_uri=image_paths))
    # with io.open(image_paths, 'rb') as image_file:
    #     content = image_file.read()
    print('In consume vision')
    image = vision.Image(content=image_paths)
    res = client.document_text_detection(image=image)
    result = res.full_text_annotation
    print('Out consume vision')
    return result