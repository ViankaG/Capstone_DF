import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
from wordcloud import  WordCloud, STOPWORDS

## Set layout of page and give browser page a title and icon.
st.set_page_config(
    page_title="BBC News Articles Visualisation",
    page_icon="📰",
    layout="centered"
)


st.title("BBC News Articles Information 📰")
## Connecting to table in Pagila database.
conn = psycopg2.connect(**st.secrets["postgres"])
cursor = conn.cursor()

user_input = st.radio("**Pick a news article category from the list:**", options=['Politics', 'Sports', 'Health and Wellbeing', 'Technology'])

## Function that returns the results for the SQL querys. The SQL querys return rows of data that relate to the categories listed in the category list.
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
    
## Function filters through the 'text' parameter, gets rid of the stopwords (e.g. to, the, a) and returns the important words. The 'more_stopwords' parameter is added
## to the list of general stopwords.
def stopwords(text, more_stopwords=[]):
    words_list = text.split()
    stopwords_list = STOPWORDS.union(set(more_stopwords))
    important_words = []

    for word in words_list:
        if word.lower() not in stopwords_list:
            important_words.append(word)

    return " ".join(important_words)

## Putting the data that is returned from the 'display_data' function into a DataFrame.
user = display_data(user_input)
col_name=['id', 'source', 'author', 'title', 'description', 'url', 'url_to_image', 'published_at', 'not_articles', 'day', 'month', 'year', 'date', 'time']
df = pd.DataFrame(user, columns=col_name)

## Iterating through the titles in the DataFrame and joining all the words in all the titles together.
df_titles = []
for title in df.title.dropna():
    df_titles.append(title)

join_words = " ".join(df_titles)


split_words = join_words.split()
word_df = pd.DataFrame({'Word': split_words})
## Grouping each word in the word DataFrame and finding the number of times they are repeated in the word DataFrame. The index is reset to normal values (e.g. 0, 1, 2, 
## etc.) and the column including the number of times a word is repeated in the word DataFrame is renamed to 'Count'. The data in the word DataFrame is then sorted 
## according to the 'Count' column.
word_count = word_df.groupby('Word').size().reset_index(name='Count').sort_values('Count', ascending=False)
## Returns the first 50 rows of the word DataFrame, which are the words with the highest count values, and converts it to a list.
highest_count_words = word_count['Word'].head(50).tolist()

standard_stopwords = st.sidebar.checkbox("Get rid of standard stopwords", False)
select_stopwords = st.sidebar.multiselect("Add more stopwords to get rid of:", sorted(highest_count_words))
width_fig = st.sidebar.slider("Select width of word cloud", 400, 2000, 1200, 50)
height_fig = st.sidebar.slider("Select height of word cloud", 200, 2000, 800, 50)

## If the 'standard_stopwords' checkbox is selected, then add the stopwords selected by user in the 'select_stopwords' multiselect feature to the list of general
## stopwords. 
## If checkbox is not selected, use the stopwords selected by user in the 'select_stopwords' multiselect feature.
if standard_stopwords:
    every_stopword = STOPWORDS.union(set(select_stopwords))
else:
    every_stopword = set(select_stopwords)

filtered_text = stopwords(join_words, every_stopword)

## Inputting the necessary settings for wordcloud and displaying it.
st.subheader(f"{user_input} Word Cloud")
wordcloud = WordCloud(width=width_fig, height=height_fig, background_color='white', max_words=200).generate(filtered_text)
wordcloud_fig = plt.figure(figsize=(width_fig/100, height_fig/100))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
st.pyplot(wordcloud_fig)

first_col, sec_col = st.columns(2)
articles = 0
num_not_articles = 0

with first_col:
    ## Iterating through each row in first DataFrame and counting the number of articles in the DataFrame.
    for index, row in df.iterrows():
        articles += 1

        ## If the value in the 'not_articles' column is equal to True, then execute the code in the if statement code block.
        if row.iloc[8] == True:
            num_not_articles += 1

    st.subheader("Article Information")
    st.write(f"**Number of articles**: {articles - num_not_articles}")
    st.write(f"**Number of videos/broadcasts**: {num_not_articles}")

with sec_col:
    st.subheader(f"{user_input} Word Count Table")
    filtered_words = filtered_text.split()
    ## Creating a DataFrame for the important words from all the titles of all the articles.
    filtered_words_df = pd.DataFrame({'Word': filtered_words})
    ## Returns a table with the number of times the important words are repeated in the DataFrame and sorts the table according to the 'Count' column.
    filtered_word_count = filtered_words_df.groupby('Word').size().reset_index(name='Count').sort_values(by='Count', ascending=False)
    st.write(filtered_word_count)


date = st.date_input("**Pick a date**")

col1, col2 = st.columns(2)
with col1:
    st.header(f"Titles of {user_input} Articles")
    for index, row in df.iterrows():
        ## If the date the user picked is equal to the value in the 'date' column in the first DataFrame, then display the value in the 'title' column.
        if date == row.iloc[12]:
            st.write(row.iloc[3])

with col2:
    st.header(f"URL of {user_input} Articles")
    for index, row in df.iterrows():
        ## If the date the user picked is equal to the value in the 'date' column in the first DataFrame, then display the value in the 'url' column.
        if date == row.iloc[12]:
            st.write(row.iloc[5])
