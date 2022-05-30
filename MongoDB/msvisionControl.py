from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import time

# region = os.environ['ACCOUNT_REGION']
# key = os.environ['ACCOUNT_KEY']
key = "144e87a649a849d0812dff38fbed311b"
region ="eastus"

credentials = CognitiveServicesCredentials(key)
client = ComputerVisionClient(
    endpoint="https://" + region + ".api.cognitive.microsoft.com/",
    credentials=credentials
)

def consumeVision(image_paths):    
    rawHttpResponse = client.read(image_paths, language="en", raw=True)
    time.sleep(2)
    numberOfCharsInOperationId = 36
    operationLocation = rawHttpResponse.headers["Operation-Location"]
    idLocation = len(operationLocation) - numberOfCharsInOperationId
    operationId = operationLocation[idLocation:]
    r = client.get_read_result(operationId)

    return r.analyze_result