import streamlit as st
import pandas as pd
import requests
import numpy as np
from PIL import Image
import tensorflow as tf
import seaborn as sns
import matplotlib.pyplot as plt
from skimage import io
from skimage.transform import resize


#Use the full page instead of a narrow central column
st.set_page_config(page_title='Recipify',
                page_icon = '🍲',
                layout = 'wide',
                initial_sidebar_state = 'expanded')

tab1, tab2 = st.tabs(["Recipify", "Team"])

with tab1:
    #set background
    import base64

    @st.cache
    def load_image(path):
        with open(path, 'rb') as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        return encoded

    def image_tag(path):
        encoded = load_image(path)
        tag = f'<img src="data:image/png;base64,{encoded}">'
        return tag

    def background_image_style(path):
        encoded = load_image(path)
        style = f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
        }}
        </style>
        '''
        return style

    st.write(background_image_style('back_yellow4.png'), unsafe_allow_html=True)


    st.markdown(
        """
    <style>
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf,#2e7bcf);
        color: white;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


    with st.sidebar:
        st.header("Recipify your picture")
        st.markdown('Upload a picture/screenshot of a cooked meal and get the recipe.')
        uploaded_file = st.file_uploader("Choose a food picture", type = ['png', 'jpg', 'jpeg'])

        recipe_button = st.button("Recipify my picture")


    st.sidebar.image('logo6.png', use_column_width=True)


    # Space out the maps so the first one is 2x the size of the other three
    #col1, col2= st.columns((6, 1))
    col1, col2, col3= st.columns((7, 3, 2))

    url = 'https://recipify-llestxp3ga-ew.a.run.app'

    with col1:
        st.header("Welcome to Recipify")
        st.subheader("You see something yummy?")
        st.subheader("🍲 ➟ 📸 ➟ 📜\nTake a picture and find the recipe on the spot!")

        if uploaded_file is not None:
        # display image:
            st.image(uploaded_file, width= 500)

            # To read image file buffer as a PIL Image:
            img = Image.open(uploaded_file)
            img1 = img.convert(mode="RGB")


            # To convert PIL Image to numpy array:
            # Transform image to tensor
            img_tensor = np.array(img1)/255.
            img_tensor = resize(img_tensor, (128, 128))
            img_tensor = tf.convert_to_tensor(img_tensor)

            img_tensor = tf.expand_dims(img_tensor, axis = 0)

            # Check the shape of img_tensor:
            # Should output shape: (number, height, width, channels)
            #st.write(img_tensor.shape)
            #st.write(type(img_tensor))  # Should output: <class 'tensorflow.python.framework.ops.EagerTensor'>
            #st.write(img_tensor[0])


        if 'load_state' not in st.session_state:
            st.session_state.load_state = False
        if recipe_button or st.session_state.load_state:
            st.session_state.load_state = True
            with st.spinner("Generating recipe based on image..."):
                #img = requests.post(url + '/predict')
                img = requests.post(url + '/predict', files = {'img': img_tensor})

                print(img.status_code)
                res = img.json()

            if 'error_message' in res.keys():
                name = res['name']
                recipe_title = f"""
                <span style="color:#f38eb4;font-family:sans-serif;font-size:25px;" >{name.capitalize()}</span>
                """
                st.markdown(recipe_title, unsafe_allow_html=True)
                st.error(f"We predict the image you uploaded to be **{res['name']}**. {res['error_message']}")

            else:
                #st.balloons()
                prediction1 = res['prediction1']
                pred_dish = res['pred_dish']
                name = res['name']
                steps = res['steps']
                rating = res['rating']
                ingredients = res['ingredients']
                calories = res['calories']
                total_fat = res['total fat']
                sugar = res['sugar']
                sodium = res['sodium']
                protein = res['protein']
                saturated_fat = res['saturated fat']
                carbohydrates = res['carbohydrates']

                prediction2 = res['prediction2']
                pred_dish_2 = res['pred_dish_2']
                name2 = res['name2']
                steps2 = res['steps2']
                rating2 = res['rating2']
                ingredients2 = res['ingredients2']
                calories2 = res['calories2']
                total_fat2 = res['total fat2']
                sugar2 = res['sugar2']
                sodium2 = res['sodium2']
                protein2 = res['protein2']
                saturated_fat2 = res['saturated fat2']
                carbohydrates2 = res['carbohydrates2']

                st.warning(f"""
                        With **{round(prediction1*100,2)}%** probability, we predict the image you uploaded to be **{pred_dish}**.
                        With **{round(prediction2*100,2)}%** probability, the uploaded image could also be **{pred_dish_2}**.
                        Maybe, you would like to try out this recipe:
                        """)

                select_dish = st.selectbox('For which of the predicted dishes would you like to see a recipe?', (pred_dish, pred_dish_2))
                if select_dish == pred_dish:
                    recipe_title = f"""
                    <span style="color:#f38eb4;font-family:sans-serif;font-size:25px;" >{name.capitalize()}</span>
                    """
                    st.markdown(recipe_title, unsafe_allow_html=True)
                    step = steps.split(',')
                    sp = ''
                    n = 3
                    chunks = [step[i:i+n] for i in range(0, len(step), n)]
                    for x in chunks:
                        s = ''.join(x)
                        sp += "1. " + s + "\n"
                    st.markdown(sp)

                    nutrition_title = '<p style="font-family:sans-serif; color:#f38eb4; font-size: 25px;">Nutritional Information</p>'
                    st.markdown(nutrition_title, unsafe_allow_html=True)
                    total = [81.5, 60, 300, 31, 2300]
                    x = [float(total_fat)/total[0]*100, float(protein)/total[1]*100, float(carbohydrates)/total[2]*100, float(sugar)/total[3]*100, float(sodium)/total[4]*100]
                    y = ['total fat', 'protein', 'carbohydrates', 'sugar', 'sodium']
                    sns.set(rc={'axes.facecolor': (0,0,0,0), 'figure.facecolor':(0,0,0,0)})
                    #sns.set_style("darkgrid")
                    fig, ax = plt.subplots() #solved by adding this line
                    ax = sns.barplot(x=x, y=y, color="#FFDCA6") #.set(title='Nutritional Values') palette = 'rocket'
                    ax.grid(axis = 'x', color='#96969A', linewidth=0.5)
                    ax.set(xlabel = "% of daily recommended intake")
                    #plt.xticks(rotation=45)
                    st.pyplot(fig)


                    with col2:
                        st.markdown('#')
                        st.markdown('#')
                        st.markdown('#')
                        st.markdown('#')
                        st.markdown('#')
                        st.markdown('#')
                        st.markdown('#')
                        rating_title = '<p style="font-family:sans-serif; color:#f38eb4; font-size: 25px;">Rating</p>'
                        st.markdown(rating_title, unsafe_allow_html=True)
                        if rating >0 and rating <2:
                            st.markdown("### ★☆☆☆☆")
                        if rating >=2 and rating <3:
                            st.markdown("### ★★☆☆☆")
                        if rating >=3 and rating <4:
                            st.markdown("### ★★★☆☆")
                        if rating >=4 and rating <5:
                            st.markdown("### ★★★★☆")
                        if rating >=5:
                            st.markdown("#### ★★★★★")


                        ingredients_title = '<p style="font-family:sans-serif; color:#f38eb4; font-size: 25px;">Ingredients</p>'
                        st.markdown(ingredients_title, unsafe_allow_html=True)
                        lst = ingredients.split(',')
                        s = ''
                        for i in lst:
                            s += "- " + i + "\n"
                        st.markdown(s)

                        calories_title = '<p style="font-family:sans-serif; color:#f38eb4; font-size: 25px;">Calories</p>'
                        st.markdown(calories_title, unsafe_allow_html=True)
                        if calories < 750:
                            st.markdown(f'**{calories}**  🟢⚪️⚪️') #based on men/women daily average 2250 recommended calories per day; divided by 3 = 750
                        elif calories >=750 and calories < 1500:
                            st.markdown(f'**{calories}**   ⚪️🟠⚪️')
                        else:
                            st.markdown(f'**{calories}**  ⚪️⚪️🔴')



                if select_dish == pred_dish_2:
                    recipe_title2 = f"""
                    <span style="color:#f38eb4;font-family:sans-serif;font-size:25px;" >{name2.capitalize()}</span>
                    """
                    st.markdown(recipe_title2, unsafe_allow_html=True)
                    step2 = steps2.split(',')
                    sp2 = ''
                    n2 = 3
                    chunks2 = [step2[i:i+n2] for i in range(0, len(step2), n2)]
                    for x in chunks2:
                        s2 = ''.join(x)
                        sp2 += "1. " + s2 + "\n"
                    st.markdown(sp2)

                    nutrition_title2 = '<p style="font-family:sans-serif; color:#f38eb4; font-size: 25px;">Nutritional Information</p>'
                    st.markdown(nutrition_title2, unsafe_allow_html=True)
                    total = [81.5, 60, 300, 31, 2300]
                    x2 = [float(total_fat2)/total[0]*100, float(protein2)/total[1]*100, float(carbohydrates2)/total[2]*100, float(sugar2)/total[3]*100, float(sodium2)/total[4]*100]
                    y = ['total fat', 'protein', 'carbohydrates', 'sugar', 'sodium']
                    sns.set(rc={'axes.facecolor': (0,0,0,0), 'figure.facecolor':(0,0,0,0)})
                    #sns.set_style("darkgrid")
                    fig, ax = plt.subplots() #solved by adding this line
                    ax = sns.barplot(x=x2, y=y, color="#FFDCA6") #.set(title='Nutritional Values') palette = 'rocket'
                    ax.grid(axis = 'x', color='#96969A', linewidth=0.5)
                    ax.set(xlabel = "% of daily recommended intake")
                    #plt.xticks(rotation=45)
                    st.pyplot(fig)


                    with col2:
                        st.markdown('#')
                        st.markdown('#')
                        st.markdown('#')
                        st.markdown('#')
                        st.markdown('#')
                        st.markdown('#')
                        st.markdown('#')
                        rating_title2 = '<p style="font-family:sans-serif; color:#f38eb4; font-size: 25px;">Rating</p>'
                        st.markdown(rating_title2, unsafe_allow_html=True)
                        if rating2 >0 and rating2 <2:
                            st.markdown("### ★☆☆☆☆")
                        if rating2 >=2 and rating2 <3:
                            st.markdown("### ★★☆☆☆")
                        if rating2 >=3 and rating2 <4:
                            st.markdown("### ★★★☆☆")
                        if rating2 >=4 and rating2 <5:
                            st.markdown("### ★★★★☆")
                        if rating2 >=5:
                            st.markdown("#### ★★★★★")


                        ingredients_title2 = '<p style="font-family:sans-serif; color:#f38eb4; font-size: 25px;">Ingredients</p>'
                        st.markdown(ingredients_title2, unsafe_allow_html=True)
                        lst2 = ingredients2.split(',')
                        s2 = ''
                        for i in lst2:
                            s2 += "- " + i + "\n"
                        st.markdown(s2)

                        calories_title2 = '<p style="font-family:sans-serif; color:#f38eb4; font-size: 25px;">Calories</p>'
                        st.markdown(calories_title2, unsafe_allow_html=True)
                        if calories2 < 750:
                            st.markdown(f'**{calories2}**  🟢⚪️⚪️') #based on men/women daily average 2250 recommended calories per day; divided by 3 = 750
                        elif calories2 >=750 and calories2 < 1500:
                            st.markdown(f'**{calories2}**   ⚪️🟠⚪️')
                        else:
                            st.markdown(f'**{calories2}**  ⚪️⚪️🔴')



with tab2:
    col1, col2, col3 = st.columns((4, 4, 2))

    with col1:
        st.markdown('## Meet the Recipify Team')
        st.markdown('#### Mariia Morskovatykh 🥨')
        st.image('Mariia.png', width = 250)
        st.markdown('#')
        st.markdown('#### Anna-Lisa Heilscher 🍭')
        st.image('Lisa1.png', width = 250)

    with col2:
        st.markdown('#')
        st.markdown('#')
        st.markdown('#### Malory Corteso 🥐')
        st.image('Malory.png', width = 250)
        st.markdown('#')
        st.markdown('#### David Kohn 🌶')
        st.image('David1.png', width = 250)
