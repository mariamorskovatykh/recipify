from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile

import pandas as pd
import tensorflow as tf
import numpy as np
from keras.models import load_model
from skimage import io
from skimage.transform import resize


app = FastAPI()

#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["*"],  # Allows all origins
#    allow_credentials=True,
#    allow_methods=["*"],  # Allows all methods
#    allow_headers=["*"],  # Allows all headers
#)

app.state.model = load_model("xception_continued_save_at_17.keras")
#We want to avoid loading the heavy Deep Learning model from MLflow at each GET request!
#The trick is to load the model into memory on startup and store it in a global variable in app.state,
# which is kept in memory and accessible across all routes!


@app.post("/predict")
async def predict(img: UploadFile = File(...)): #later: def predict(img_tensor)
    #preprocessing in frontend (turned into tensor and normalized and resized to 156*156)
    img_tensor = await img.read()
    img_tensor = tf.io.decode_raw(input_bytes = img_tensor, out_type = tf.float64)
    img_tensor = tf.reshape(img_tensor, [1, 128, 128, 3])

    y_pred = app.state.model.predict(img_tensor)
    prediction = pd.DataFrame(y_pred, columns= range(251))
    prediction = prediction.T
    prediction = round(prediction.sort_values(by=0), 5)

    #y_pred = np.random.uniform(0,1,251) #dummy pred
    max_class_single = np.argmax(y_pred)
    second_pred_class = np.argsort(y_pred[0])[-2]

    list_recipe_df = pd.read_fwf('class_list.txt', header=None)
    list_recipe_df.columns =['Name']
    list_recipe_df['Name'] = list_recipe_df['Name'].str.replace('\d+', '')
    list_recipe_df['Name'] = list_recipe_df['Name'].str.replace('_', ' ')
    list_recipe = []
    for recipe in list_recipe_df['Name']:
        recipe = recipe.replace('food', '')
        recipe = recipe.replace('macaron', 'macarons')
        recipe = recipe.strip()
        list_recipe.append(recipe)


    y_pred_dish = list_recipe[max_class_single]
    second_y_pred_dish = list_recipe[second_pred_class]
    recipe_df = pd.read_csv('recipe.csv')
    selected_recipes = recipe_df[recipe_df['name'].str.contains(y_pred_dish).fillna(False)]
    filter1 = (selected_recipes["rating"].max())
    selected_recipes = selected_recipes[selected_recipes['rating'] == filter1]
    selected_recipes2 = recipe_df[recipe_df['name'].str.contains(second_y_pred_dish).fillna(False)]
    filter2 = (selected_recipes2["rating"].max())
    selected_recipes2 = selected_recipes2[selected_recipes2['rating'] == filter2]


    if len(selected_recipes) and len(selected_recipes2) > 0:
        output =  {'pred_dish': y_pred_dish, 'prediction1': float(prediction.iat[-1, 0]), 'name': selected_recipes.iloc[0][0], 'minutes':int(selected_recipes.iloc[0][2]), 'n_steps': int(selected_recipes.iloc[0][4]),\
            'n_ingredients': int(selected_recipes.iloc[0][7]), 'ingredients':selected_recipes.iloc[0][6], 'steps':selected_recipes.iloc[0][5], 'calories':selected_recipes.iloc[0][8],\
             'total fat': selected_recipes.iloc[0][9], 'sugar': selected_recipes.iloc[0][10], 'sodium': selected_recipes.iloc[0][11], 'protein': selected_recipes.iloc[0][12],\
            'saturated fat': selected_recipes.iloc[0][13], 'carbohydrates': selected_recipes.iloc[0][14], 'rating': int(selected_recipes.iloc[0][15]),\
            'pred_dish_2': second_y_pred_dish, 'prediction2': float(prediction.iat[-2, 0]), 'name2': selected_recipes2.iloc[0][0], 'minutes2':int(selected_recipes2.iloc[0][2]), 'n_steps2': int(selected_recipes2.iloc[0][4]),\
            'n_ingredients2': int(selected_recipes2.iloc[0][7]), 'ingredients2':selected_recipes2.iloc[0][6], 'steps2':selected_recipes2.iloc[0][5], 'calories2':selected_recipes2.iloc[0][8],\
             'total fat2': selected_recipes2.iloc[0][9], 'sugar2': selected_recipes2.iloc[0][10], 'sodium2': selected_recipes2.iloc[0][11], 'protein2': selected_recipes2.iloc[0][12],\
            'saturated fat2': selected_recipes2.iloc[0][13], 'carbohydrates2': selected_recipes2.iloc[0][14], 'rating2': int(selected_recipes2.iloc[0][15])}
        return output

    #elif len(selected_recipes) == 0:
    #    error_message = {'name': y_pred_dish, "error_message": "Unfortunately, there is no recipe available for this dish right now. Come back later to check again."}
    #    return error_message
    else:
        error_message2 = {'name': second_y_pred_dish, "error_message": "Unfortunately, there is no recipe available for this dish right now. Come back later to check again."}
        return error_message2


@app.get("/")
def root():
    return {
    'greeting': 'Hello'
}
