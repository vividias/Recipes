import streamlit as st
import pandas as pd
from services.google_api import RECIPES_DB_SHEET_ID, sheets_service
from main import get_recipes_text

st.set_page_config(layout="wide")
st.title('Recipes')

st.header('Insert new recipe')

def on_change_recipe_text():
    with st.spinner('Getting the new recipe...'):
        get_recipes_text(text = st.session_state["recipe_text"], image_url = None, video_url = None)
    st.session_state["recipe_text"] = ''
    st.success("Inserted new recipe!")

recipe_txt = st.empty()
recipe_txt.text_area(label = 'Insert a recipe text with steps and ingredients.', key="recipe_text")

st.button("Insert", on_click=on_change_recipe_text)


st.header('Database')

def load_data():

    sheets_db = sheets_service.open_by_key(RECIPES_DB_SHEET_ID).sheet1
    data = sheets_db.get_all_records()
    if len(data)==0:
        columns = sheets_db.get_all_values()[0]
        df_sheets_DB = pd.DataFrame(columns=columns)
    else:
        columns = list(data[0].keys())
        df_sheets_DB = pd.DataFrame(data)
    return df_sheets_DB

df = load_data()
df.pop('post_id')

df_config_dict = {}

link_columns = ['post_video_url', 'doc_link']
for link_column in link_columns:
    df_config_dict[link_column] = st.column_config.LinkColumn()

rating_column = 'rating'
df_config_dict[rating_column] =  st.column_config.NumberColumn(format="%d ⭐")

st.dataframe(
    df,
    column_config=df_config_dict,
    hide_index=True,
)