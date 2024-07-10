import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
from wordcloud import  WordCloud, STOPWORDS

st.set_page_config(
    page_title="BBC News Articles Visualisation",
    page_icon="📰",
    layout="centered"
)


st.title("BBC News Articles Information 📰")
conn = psycopg2.connect(**st.secrets["postgres"])
cursor = conn.cursor()

user_input = st.radio("**Pick a news article category from the list:**", options=['Politics', 'Sports', 'Health and Wellbeing', 'Technology'])


def display_data(category):
    if category == 'Politics':
        cursor.execute("""SELECT *
                    FROM student.capstone_vg_final 
                    WHERE description ILIKE ANY(ARRAY['%labour%', '%campaign%', '%conservative%', '%election%', '%president%', '%prime minister%', '%parliament%', '%candidate%']);
                    """)
        return cursor.fetchall()
    elif category == 'Sports':
        cursor.execute("""SELECT *
                    FROM student.capstone_vg_final 
                    WHERE description ILIKE ANY(ARRAY['%euro%', '%england%', '%team-mates%', '%wimbledon%']);
                    """)
        return cursor.fetchall()
    elif category == 'Health and Wellbeing':
        cursor.execute("""SELECT *
                    FROM student.capstone_vg_final 
                    WHERE description ILIKE ANY(ARRAY['%nhs%', '%covid%', '%health%', '%cancer%', '%condition%', '%hospital%', '%illness%', '%accessible%']);
                    """)
        return cursor.fetchall()
    else:
        cursor.execute("""SELECT *
                        FROM student.capstone_vg_final 
                        WHERE description ILIKE ANY(ARRAY['%apps%', '%ai-powered%']);
                        """)
        return cursor.fetchall()
    

def stopwords(text, more_stopwords=[]):
    words_list = text.split()
    stopwords_list = STOPWORDS.union(set(more_stopwords))
    important_words = []

    for word in words_list:
        if word.lower() not in stopwords_list:
            important_words.append(word)

    return " ".join(important_words)


user = display_data(user_input)
col_name=['id', 'source', 'author', 'title', 'description', 'url', 'url_to_image', 'published_at', 'not_articles', 'day', 'month', 'year', 'date', 'time']
df = pd.DataFrame(user, columns=col_name)

df_titles = []
for title in df.title.dropna():
    df_titles.append(title)

join_words = " ".join(df_titles)

split_words = join_words.split()
word_df = pd.DataFrame({'Word': split_words})
word_count = word_df.groupby('Word').size().reset_index(name='Count').sort_values('Count', ascending=False)
highest_count_words = word_count['Word'].head(50).tolist()

standard_stopwords = st.sidebar.checkbox("Get rid of standard stopwords", False)
select_stopwords = st.sidebar.multiselect("Add more stopwords to get rid of:", sorted(highest_count_words))
width_fig = st.sidebar.slider("Select width of word cloud", 400, 2000, 1200, 50)
height_fig = st.sidebar.slider("Select height of word cloud", 200, 2000, 800, 50)

if standard_stopwords:
    every_stopword = STOPWORDS.union(set(select_stopwords))
else:
    every_stopword = set(select_stopwords)

filtered_text = stopwords(join_words, every_stopword)

st.subheader(f"{user_input} Word Cloud")
wordcloud = WordCloud(width=width_fig, height=height_fig, background_color='white', max_words=200, contour_width=3, contour_color='steelblue').generate(filtered_text)
wordcloud_fig = plt.figure(figsize=(width_fig/100, height_fig/100))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
st.pyplot(wordcloud_fig)

first_col, sec_col = st.columns(2)
articles = 0
num_not_articles = 0

with first_col:
    for index, row in df.iterrows():
        articles += 1

        if row.iloc[8] == True:
            num_not_articles += 1

    st.subheader("Article Information")
    st.write(f"**Number of articles**: {articles - num_not_articles}")
    st.write(f"**Number of videos/broadcasts**: {num_not_articles}")

with sec_col:
    st.subheader(f"{user_input} Word Count Table")
    filtered_words = filtered_text.split()
    filtered_words_df = pd.DataFrame({'Word': filtered_words})
    filtered_word_count = filtered_words_df.groupby('Word').size().reset_index(name='Count').sort_values(by='Count', ascending=False)
    st.write(filtered_word_count)


date = st.date_input("**Pick a date**")

col1, col2 = st.columns(2)
with col1:
    st.header(f"Titles of {user_input} Articles")
    for index, row in df.iterrows():
        if date == row.iloc[12]:
            st.write(row.iloc[3])

with col2:
    st.header(f"URL of {user_input} Articles")
    for index, row in df.iterrows():
        if date == row.iloc[12]:
            st.write(row.iloc[5])