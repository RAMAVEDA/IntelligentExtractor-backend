import os,environ
from sendgrid import SendGridAPIClient

import base64

from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

env = environ.Env()

environ.Env.read_env()

# client = storage.Client.from_service_account_json(
#     json_credentials_path=env(''))

os.environ['EMAIL_API_KEY'] = env('EMAIL_KEY')


def emailTrigger(model, filepath, filename):
    message = Mail(
    from_email='interltester@gmail.com',
    to_emails='shakthiprakash1509@gmail.com',
    subject='Extraction Results for ' + model,
    html_content="Please find the attachments of extraction results for " + model)

    with open(filepath, 'rb') as f:
        data = f.read()
        f.close()
    encoded_file = base64.b64encode(data).decode()

    
    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName('01e36990-6a13-4f2d-ae81-41c63d66654c.csv'),
        FileType('application/csv'),
        Disposition('attachment')
    )
    message.attachment = attachedFile
    # Create SMTP session for sending the mail
    sg = SendGridAPIClient(os.environ.get('EMAIL_API_KEY'))
    response = sg.send(message)
    return response
