# Purpose

Your favorites recipes all in the same place and in the same format! 
Create a DB with all of the recipes with a link to a document for each one, based on a document template.
Retrieve recipes from posts of a private collection in Instagram or from any text you copy from a link.


# Get ready

- Install the packages in "requirements.txt": pip install -r requirements

## Google services
- Activate you Google API for Sheets, Docs and Drive in Google Cloud
- Get your service account json from Google Cloud so that you can access the Google APIs
- Add the file path of the json to the environment variable "SERVICE_ACCOUNT_FILE"
- Everything created in the Google Drive will be from the user of the Google API project of Google Cloud
- Add the email that should have access to the recipe docs in environment variable "SHARE_EMAIL"

## Recipe Template
- Create a doc template of what you want the recipe docs to look like
- It must have the following string, that will be used to be replaced by the actual recipe information:
    - "<Title>"
    - "<ListIngredients>"
    - "<NumberedSteps>"
- After creating the template doc, have the document_id in the following environment variable "RECIPES_TEMPLATE_DOC_ID"
- Create also a sheet DB file (make sure the Google Cloud project user has access to it), with the following columns (in order):
    - post_id
    - post_video_url
    - recipe_name
    - recipe_category
    - doc_link
    - (you can add any more that you like after the above ones, it won't break the code)
- Have the sheet DB id in the environment variable "RECIPES_DB_SHEET_ID"

## OpenAI
- For this project you need an OpenAI account to convert the recipes text into the format needed
- Have the API key and the organization id in the enviroment variables "OPENAI_API_KEY" and "OPENAI_ORGANIZATION"

## Instagram (Optional)
Only if you want to be able to get recipes from instagram collections.
- Get all your recipes posts in a private collection in Instagram named "Recipes"
- Add your instagram username and password into the environment variables "ACCOUNT_USERNAME" and "ACCOUNT_PASSWORD"
- The code will use a package named "instagrapi"
- WARNING: Instagram may not like the automated bot entering your account
- The maximum posts the instagrapi can see in a collection is 21 by default, after installing the package, change the default amount of "collection_medias" in "instagrapi/mixins/collection.py" to a bigger max


# Future Work
- Make more variables configurable
- Improve code robustness 
- Get recipes from input url
- Get the recipes from image of a recipe book
- Add the ability to choose different templates