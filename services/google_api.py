import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import os
from pathlib import Path
from dotenv import load_dotenv
import requests


dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

RECIPES_TEMPLATE_DOC_ID = os.getenv('RECIPES_TEMPLATE_DOC_ID')
RECIPES_DB_SHEET_ID = os.getenv('RECIPES_DB_SHEET_ID')
SHARE_EMAIL = os.getenv('SHARE_EMAIL')
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/spreadsheets']

drive_creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=drive_creds)

docs_creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
docs_service = build('docs', 'v1', credentials=docs_creds)

sheets_creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = gspread.authorize(sheets_creds)


def find_folder_by_name(drive_service, folder_name):
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)", spaces='drive').execute()
    folders = results.get('files', [])
    
    if folders:
        print(f'Folder "{folder_name}" already exists with ID: {folders[0]["id"]}')
        return folders[0]['id']
    return None


def create_google_doc(drive_service, title):
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.document'
    }
    file = drive_service.files().create(body=file_metadata, fields='id').execute()
    print(f'Created document with ID: {file.get("id")}')
    return file.get('id')


def create_google_doc_in_folder(drive_service, title, folder_id):
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [folder_id]
    }
    file = drive_service.files().create(body=file_metadata, fields='id').execute()
    print(f'Created document with ID: {file.get("id")} inside folder with ID: {folder_id}')
    return file.get('id')


def share_document(drive_service, document_id, email):
    permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': email
    }
    drive_service.permissions().create(
        fileId=document_id,
        body=permission,
        fields='id'
    ).execute()
    print(f'Shared document with {email}')


def share_folder(drive_service, folder_id, email):
    permission = {
        'type': 'user', 
        'role': 'writer',
        'emailAddress': email
    }

    drive_service.permissions().create(
        fileId=folder_id,
        body=permission,
        fields='id'
    ).execute()

    print(f'Shared folder {folder_id} with user')

def create_find_google_folder(drive_service, folder_name, email):
    folder_id = find_folder_by_name(drive_service, folder_name)
    
    if folder_id:
        return folder_id
    
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
    print(f'Created folder with ID: {folder.get("id")}')
    folder_id = folder.get('id')
    share_folder(drive_service=drive_service, folder_id=folder_id, email=email)
    return folder_id

def delete_document(drive_service, document_id):
    try:
        drive_service.files().delete(fileId=document_id).execute()
        print(f"Document with ID {document_id} has been deleted.")
    except Exception as e:
        print(f"An error occurred: {e}")


def upload_image_to_drive(drive_service, image_url, image_name):
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception("Failed to download image. Status code: {}".format(response.status_code))
    image_data = io.BytesIO(response.content)

    media = MediaIoBaseUpload(image_data, mimetype='image/jpeg')
    file_metadata = {
        'name': image_name,
        'mimeType': 'image/jpeg' 
    }
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = file.get('id')

    drive_service.permissions().create(
        fileId=file_id,
        body={
            'type': 'anyone',
            'role': 'reader'
        }
    ).execute()

    return file_id


def copy_template(drive_service, template_doc_id, new_title):
    body = {
        'name': new_title
    }
    copied_file = drive_service.files().copy(fileId=template_doc_id, body=body).execute()
    return copied_file['id']


def copy_template_to_folder(drive_service, template_doc_id, new_title, folder_id):
    body = {
        'name': new_title,
        'parents': [folder_id]
    }
    copied_file = drive_service.files().copy(fileId=template_doc_id, body=body).execute()
    return copied_file['id']
