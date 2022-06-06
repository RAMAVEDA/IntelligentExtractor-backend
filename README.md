
# Intelligent Extractor - Backend

A Low-Code/No-Code based Product which is scalable (hosted on Azure Kubernetes with CI CD) to enable Intelligent Data extraction to accelerate data entry for Loan Officers/other Finance product users using Computer Vision of Azure, Self Service Bot with QnA Maker for answering Financial related Questions, Prediction for Mortgage approval/House pricing - Azure ML model

## Deployment

To deploy this project run

### Required Azure Services for deployment
- Azure blob storage
- Azure computer vision
- Azure cosmos DB
- Azure container registry
- Azure kubernetes cluster 

### Conifugration changes

.env file avialble inside extractor/

- Create a Azure blob storage with blob and add BLOB_NAME, CONNECTION_STRING, ACCOUNT_NAME and ACCOUNT_KEY to .env file 
  ```bash
    BUCKET='<BLOB_NAME>'
    connect_str='<CONNECTION_STRING>'
    AccountName='<ACCOUNT_NAME>'
    AccountKey='<ACCOUNT_KEY>'
  ```
- Enable Azure Computer Vision API and add ACCOUNT_REGION and ACCOUNT_KEY_VISION to .env file
  ```bash
    ACCOUNT_REGION='<ACCOUNT_REGION>'
    ACCOUNT_KEY_VISION='<ACCOUNT_KEY_VISION>'
  ```
- Create Azure cosmos DB and add its endpoint, USERNAME and PASSWORD to .env file
  ```bash
    HOST_COSMOS='<endpoint>'
    USERNAME_COSMOS='<USERNAME>'
    PASSWORD_COSMOS='<PASSWORD>'
  ```

### Deployment steps
  ```bash
    git clone https://github.com/RAMAVEDA/IntelligentExtractor-backend.git
    cd IntelligentExtractor-backend
    docker build -t intelligentextrator-backend .
    docker tag intelligentextrator-backend {username}/intelligentextrator-backend
    docker login 
    docker push  {username}/intelligentextrator-backend
    Create deployment.yml(point to docker image : {username}/intelligentextrator-backend) and service.yml
    kubectl apply -f deployment.yml
    kubectl apply -f service.yml
  ```
## Authors

- [@RAMAKRISHNAN VEDANARAYANAN](https://github.com/RAMAVEDA)
- [@SAKTHI PRAKASH](https://github.com/sha1509)

