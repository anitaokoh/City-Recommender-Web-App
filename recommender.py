# import libriaries
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import time
from sklearn.metrics.pairwise import cosine_similarity

# import the data and create revelent dataframes
def load():
    df = pd.read_csv('city_ranking.csv')
    data = df.set_index('city'). iloc[:,1:-1]
    scores = df.set_index('city'). iloc[:,1:-1].round().astype(int)
    location = []
    for index, city, country in df[["city", "country"]].sort_values("country").itertuples():
        new = f'{city}, {country}'
        location.append(new)
    return df, data,scores, location

#Calculate the cosine-similarity
def find_similarity(column, user, number,scores, city):
    if city == 'Others':
        new_df = scores[column]
    else:
        locate = city.split(',')
        new_df = scores[scores.index !=  locate[0]][column]
    value = []
    for index,city in enumerate(new_df.index):
        city_old = new_df.loc[city].values.reshape(-1,number)
        user = user.reshape(-1, number)
        score = cosine_similarity(city_old, user)
        value.append(score)
    similarity = pd.Series(value, index=new_df.index)
    city_similar = similarity.sort_values(ascending=False).astype(float).idxmax()
    # message = f'Based on your aggregate preferences and ratings, {city_similar} is the top recommended city to move/travel to.'
    return city_similar

# Get more info about the recommended city
def final_answer(df,word, data):
    title = f'About {word}'
    subtitle = 'City Ranking in terms of Business, essentials, Openness and recreation scores(over 10.0)'
    country = df.loc[df['city'] == word, 'country'].iloc[0]
    if word in df['city'].head().values:
        response = "It is actually one of the top 5 cities that has piqued millennials' interests."
    elif word in df['city'].head(10).values:
        response = "It is actually one of the top 10 cities that has piqued millennials' interests."
    elif word in df['city'].tail(5).values:
        response = "It is actually one of the least 5 cities that has piqued millennials' interests."
    else:
        response = ""

    ranking = list(zip(list(data.loc[word].index),data.loc[word]))
    breakdown = pd.DataFrame(ranking, columns = ['Category','Score'])
    breakdown['Score'] = breakdown['Score'].round(1)

    return title, country , subtitle, response, breakdown

#The app controller
def main():
    st.title('City Recommender')
    # st.write(intro)
    # image= Image.open('unsplash2.jpg')
    # st.image(image, use_column_width=True)
    html_temp = """
    <div style="background-color:Turquoise;padding:13px">
    <p>The frequency at which people move from city to city has been growing.
    It is becoming cheaper to move around to the extent that <b>Cost of Moving</b> is becoming the least reason to move or travel.
    People leave their city for other reasons or preferences and some of these preferences have been captured in the app to <b>help recommend your next city move or travel</b>.
    Below, you get to choose 5 aspect of a city that is most important to you and then you get to rank them in terms of importance from 1 to 10.</p>
    </div>
    <br>
    """


    st.markdown(html_temp, unsafe_allow_html=True)

    df, data,scores, location = load()
    location.append('Others')
    city = st.selectbox("Location of Residence", location)
    preference = st.multiselect("Choose the 5 features that matters to you the most in a city",scores.columns)
    if st.checkbox("Rate the features"):
         if len(preference) == 5 :
            level1 = st.slider(preference[0], 1,10)
            level2 = st.slider(preference[1], 1,10)
            level3 = st.slider(preference[2], 1,10)
            level4 = st.slider(preference[3], 1,10)
            level5 = st.slider(preference[4], 1,10)
            if st.button("Recommend", key="hi"):
                user = np.array([level1, level2,level3,level4,level5])
                column = preference
                number = len(preference)
                city_similar = find_similarity(column, user, number,scores,city)
                with st.spinner("Analysing..."):
                    time.sleep(5)
                st.text(f'\n\n\n')
                st.markdown('--------------------------------------------**Recommendation**--------------------------------------------')
                st.text(f'\n\n\n\n\n\n')
                st.markdown(f'Based on your aggregate preferences and ratings, **{city_similar}** is the top recommended city to move/travel to.')
                title, country , subtitle, response, breakdown = final_answer(df, city_similar, data)
                st.text(f'\n\n\n\n\n\n')
                st.markdown(f'----------------------------------------------**{title}**---------------------------------------------')
                st.write(f'{city_similar} is a city in {country}. {response}')
                st.text(subtitle)
                st.table(breakdown.style.format({'Score':'{:17,.1f}'}).background_gradient(cmap='Blues').set_properties(subset=['Score'], **{'width': '250px'}))
                st.markdown(f'For more info on city rank scores, check [here](https://www.nestpick.com/millennial-city-ranking-2018/)')


         elif len(preference) > 5:
              st.warning("choose only 5 features")
         else:
             st.error("You are to choose at least 5 feature from the bove options")
    #the end
    if st.button("Thanks"):
          st.balloons()

if __name__ == "__main__":
    main()
