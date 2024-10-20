import os
from typing import List
from pathlib import Path
from instagrapi import Client
from instagrapi.types import Media
from dotenv import load_dotenv

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
ACCOUNT_USERNAME = os.getenv('ACCOUNT_USERNAME')
ACCOUNT_PASSWORD = os.getenv('ACCOUNT_PASSWORD')

insta_client = Client()
insta_client.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)


def recipes_collection_media(collection_name: str = 'Recipes') -> List[Media]:
    print(f'Getting media from collection {collection_name}')
    recipes_collection: List[Media] = insta_client.collection_medias_by_name(name = collection_name)
    print(f'Found {str(len(recipes_collection))} media in collection.')
    return recipes_collection