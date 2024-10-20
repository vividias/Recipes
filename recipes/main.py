import json
from instagrapi.types import Media
from recipes.schemas import Recipes, RecipeExists
from recipes.utils import recipes_replace_text_with_formatting, insert_image_at_bottom_left, download_video_url_and_upload_to_drive
from services.llm_model import LLMModel
from services.google_api import SHARE_EMAIL, drive_service, docs_service
from services.google_api import copy_template_to_folder, share_document

llm_model = LLMModel()

def create_recipes_doc(sheets_db, folder_id: str, id: str, recipes: Recipes, recipes_template_doc_id: str, video_url: str|None=None, image_url: str|None=None):
    for post_recipe in recipes.recipes:
            new_title = 'Recipe: ' + post_recipe.title.title()
            doc_id = copy_template_to_folder(drive_service, recipes_template_doc_id, new_title, folder_id)

            recipes_replace_text_with_formatting(docs_service, doc_id, post_recipe)
            print('Text replaced successfully.')

            if image_url:
                insert_image_at_bottom_left(docs_service, doc_id, image_url, drive_service)
                print('Image added successfully.')

            link_url = str(download_video_url_and_upload_to_drive(drive_service=drive_service, video_url=video_url, file_name=f'{id}.mp4')) \
                if (video_url is not None and video_url!='None') else ''
            new_row = [id,
                link_url,
                post_recipe.title.title(),
                post_recipe.category,
                f'https://docs.google.com/document/d/{doc_id}/edit']
            sheets_db.append_row(new_row)
            print('DB updated successfully.')


def extract_recipes_from_media(text: str) -> Recipes:
    #TODO: add retries

    default = Recipes(recipes = [])

    try:

        aux_prompt = 'Does the following post description has a recipe details of both the ingredients and the steps?\n' + \
            f'Post description:\n\n{text}\n\n' + \
            f'Answer in the following JSON format: {json.dumps(RecipeExists.model_json_schema())}'

        aux_output = llm_model.generate(prompt = aux_prompt, json_schema = json.dumps(RecipeExists.model_json_schema()))
        aux_answer = RecipeExists(**json.loads(aux_output))
        if not aux_answer.answer:
            print(text)
            print('No recipe found in description.')
            return default

        print('Recipe found in description.')
        prompt = 'Given the following post description of a video, retrieve the recipes mentioned, if any. Check if there are groups of ingredients for specific parts. If ingredient values are a range, choose one of the values. Translate to english if not in english.\n' + \
            f'Post description:\n\n{text}\n\n' + \
            f'Answer in the following JSON format: {json.dumps(Recipes.model_json_schema())}'

        post_recipes_output = llm_model.generate(prompt = prompt, json_schema = json.dumps(Recipes.model_json_schema()))
        post_recipes = Recipes(**json.loads(post_recipes_output))

        return post_recipes

    except Exception as e:
        print(e)
        return default


def create_post_recipes_doc(media: Media, folder_id: str, recipes_template_doc_id: str, sheets_db):

    print('Getting recipes from media post.')
    post_description = media.caption_text
    post_recipes = extract_recipes_from_media(text = post_description)

    image_url = str(media.resources[0].thumbnail_url) if (media.resources and len(media.resources)>0) \
        else str(media.thumbnail_url) 
    video_url = str(media.video_url) if media.video_url else (str(media.resources[0].video_url) if (media.resources and len(media.resources)>0) else '')

    create_recipes_doc(sheets_db=sheets_db, folder_id=folder_id, id=media.id, recipes=post_recipes,
                       recipes_template_doc_id=recipes_template_doc_id, video_url=video_url, image_url=image_url)

def create_text_recipes_doc(text: str, image_url: str|None, video_url: str|None, folder_id: str, recipes_template_doc_id: str, sheets_db):

    print('Getting recipes from text.')
    post_recipes = extract_recipes_from_media(text = text)

    image_url = image_url if image_url else ''
    video_url = video_url if video_url else ''
    id = str(hash(text))

    create_recipes_doc(sheets_db=sheets_db, folder_id=folder_id, id=id, recipes=post_recipes,
                       recipes_template_doc_id=recipes_template_doc_id, video_url=video_url, image_url=image_url)
