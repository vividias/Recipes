import requests
import io
from typing import List, Dict
from recipes import schemas as recipes_schemas
from googleapiclient.http import MediaIoBaseUpload
from services.google_api import upload_image_to_drive

def recipes_replace_text_with_formatting(docs_service, document_id, recipe: recipes_schemas.Recipe):
    requests = []

    # Locate the placeholder for the recipe title and replace it
    requests.append({
        'replaceAllText': {
            'containsText': {
                'text': '<Title>',
                'matchCase': True,
            },
            'replaceText': recipe.title.title()
        }
    })

    # Create a formatted ingredients list with groups
    ingredients_text = ''
    grouped_ingredients: Dict[str,List[recipes_schemas.Ingredient]] = {}
    
    # Group ingredients by their group
    for ingredient in recipe.ingredients:
        group = ingredient.group if ingredient.group else ''
        if group not in grouped_ingredients:
            grouped_ingredients[group] = []
        grouped_ingredients[group].append(ingredient)

    # Format the ingredients text
    for group, ingredients in grouped_ingredients.items():
        ingredients_text += f'\n{group}:\n' if group else f'\n\n'
        ingredients_text += '\n'.join([
            f"- {(ingredient.quantity)} {ingredient.measure} {ingredient.name}" 
            if (ingredient.quantity is not None and ingredient.quantity>0 and ingredient.measure is not None) else f"- {ingredient.name}" for ingredient in ingredients 
        ])
        ingredients_text += '\n'

    # Replace the ingredients list placeholder
    requests.append({
        'replaceAllText': {
            'containsText': {
                'text': '<ListIngredients>',
                'matchCase': True,
            },
            'replaceText': ingredients_text.strip()  # Remove trailing newline
        }
    })

    # Replace the steps placeholder with the formatted steps
    steps_text = '\n'.join([
        f"* Step {step.number}: {step.description}\n"
        for step in recipe.steps
    ])

    requests.append({
        'replaceAllText': {
            'containsText': {
                'text': '<NumberedSteps>',
                'matchCase': True,
            },
            'replaceText': steps_text
        }
    })
    
    # Send the requests to the Docs API
    docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()


def insert_image_at_bottom_left(docs_service, document_id, image_url, drive_service):
    # Upload the image to Google Drive and get the file ID
    image_name = 'new_image'
    image_file_id = upload_image_to_drive(drive_service, image_url, image_name)
    print('image_file_id', image_file_id)

    # Create the URL for the uploaded image
    image_url = f'https://drive.google.com/uc?id={image_file_id}'

    # Retrieve the document content to determine the document's end
    document = docs_service.documents().get(documentId=document_id).execute()
    content = document.get('body').get('content')

    # Assuming the document’s last section is the end
    last_element = content[-1]
    last_element_index = last_element.get('endIndex', 1)

    # Insert the image at the end of the document
    insert_image_requests = [{
        'insertInlineImage': {
            'location': {
                'index': last_element_index - 1,  # Start from the beginning (or adjust to a specific index)
            },
            'uri': image_url,
            'objectSize': {
            'height': {
                'magnitude': 2*72,
                'unit': 'PT'
            },
            'width': {
                'magnitude': 2*72,
                'unit': 'PT'
            }
        }
        }
    }]

    # Execute the request to insert the image
    docs_service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': insert_image_requests}
    ).execute()


def download_video_url_and_upload_to_drive(drive_service, video_url, file_name):
    # Download video from URL
    response = requests.get(video_url, stream=True)
    if response.status_code != 200:
        print("Failed to download video")
        return None

    # Convert the content into a BytesIO object (in-memory file)
    video_data = io.BytesIO()
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            video_data.write(chunk)
    
    video_data.seek(0)  # Reset file pointer to the beginning

    # Upload to Google Drive
    file_metadata = {'name': file_name}
    media = MediaIoBaseUpload(video_data, mimetype='video/mp4', resumable=True)

    # Upload the file and get its ID
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')

    # Make the file shareable
    drive_service.permissions().create(
        fileId=file_id,
        body={'role': 'reader', 'type': 'anyone'},
    ).execute()

    # Generate the shareable link
    shareable_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

    return shareable_link