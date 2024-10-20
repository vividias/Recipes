import pandas as pd
from saved_collections.insta_connection import recipes_collection_media
from services.google_api import RECIPES_DB_SHEET_ID, RECIPES_TEMPLATE_DOC_ID, drive_service, sheets_service, SHARE_EMAIL
from services.google_api import create_find_google_folder
from recipes.main import create_post_recipes_doc, create_text_recipes_doc

FOLDER_NAME = 'Recipes'

def get_recipes_insta():

    folder_id = create_find_google_folder(drive_service = drive_service, folder_name = FOLDER_NAME, email = SHARE_EMAIL)

    sheets_db = sheets_service.open_by_key(RECIPES_DB_SHEET_ID).sheet1
    data = sheets_db.get_all_records()
    if len(data)==0:
        columns = sheets_db.get_all_values()[0]
        df_sheets_DB = pd.DataFrame(columns=columns)
    else:
        columns = list(data[0].keys())
        df_sheets_DB = pd.DataFrame(data)
    DB_post_ids = list(df_sheets_DB['post_id'].values)

    collection_medias = recipes_collection_media(collection_name='Recipes')

    for collection_media in collection_medias:
        
        if collection_media.id in DB_post_ids:
            print('Media post recipes were already extracted.')

        else:
            create_post_recipes_doc(media = collection_media, folder_id = folder_id,
                                    recipes_template_doc_id = RECIPES_TEMPLATE_DOC_ID, sheets_db = sheets_db)


def get_recipes_text(text: str, image_url: str|None, video_url: str|None):

    folder_id = create_find_google_folder(drive_service = drive_service, folder_name = FOLDER_NAME, email = SHARE_EMAIL)

    sheets_db = sheets_service.open_by_key(RECIPES_DB_SHEET_ID).sheet1
    data = sheets_db.get_all_records()
    if len(data)==0:
        columns = sheets_db.get_all_values()[0]
        df_sheets_DB = pd.DataFrame(columns=columns)
    else:
        columns = list(data[0].keys())
        df_sheets_DB = pd.DataFrame(data)
    DB_post_ids = list(df_sheets_DB['post_id'].values)

    if str(hash(text)) in DB_post_ids:
        print('Text recipes were already extracted.')

    else:
        create_text_recipes_doc(text = text, image_url = image_url, video_url = video_url, folder_id = folder_id,
                                recipes_template_doc_id = RECIPES_TEMPLATE_DOC_ID, sheets_db = sheets_db)