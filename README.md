# Capstone_DF - My BBC News ETL Pipeline

# Summary
I created an ETL pipeline that collects data about BBC News articles every hour using an API. It then cleans and stores the data in a database. Finally, insights of the data are visualised in a dashboard. The main purpose of this project is to give users interesting insights about different categories of articles published on BBC News.

# Motivation
I decided to create this project because I wanted to make it easier for users to have information about BBC News articles all in one place.

# Build Status
There is a bug with the multi-select stopwords feature in my Streamlit app. You will notice that some words that are selected still show up in the "Word Count Table". This is not meant to happen.

# Important Features
I created a wordcloud in my Streamlit app that includes all of the important words from all the titles of all the articles that have been loaded into the database. When different categories of articles are selected, different wordclouds are displayed each time.

# Link To My Dashboard
https://capstonevg.streamlit.app/

# API Reference
https://newsapi.org/
