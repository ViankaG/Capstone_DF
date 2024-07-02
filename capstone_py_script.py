import pandas as pd
import requests
import os
from dotenv import load_dotenv
import psycopg2

## Loading the '.env' file that has the credentials.
load_dotenv()
## Creating variables for various credentials in '.env' file.
password = os.getenv('sql_password')
user = os.getenv('sql_user')
host_name = os.getenv('host')
api_key = os.getenv('api_key')

## URL of chosen API
url = f'https://newsapi.org/v2/everything?sources=bbc-news&apiKey={api_key}'

## Output of API in JSON format
articles = requests.get(url).json()

## Creating DataFrame and adding a column called 'id'.
news_df = pd.DataFrame(columns = ['id'])

articles_info = articles['articles']

## Creating variable for id for DataFrame. Variable is used for values in 'id' column in DataFrame.
article_id = 0

## Looping through list of articles.
for article in articles_info:
    article_id += 1
    
    source = article['source']
    author = article['author']
    
    ## Creating column names from API for DataFrame and inputting values from API into these columns.
    for key, value in article.items():
        news_df.loc[article_id, key] = str(value)
        news_df.loc[article_id, 'id'] = article_id
        
        ## Looping through items in the dictionary in the 'source' column. Changing the value in the 'source' column to return a name instead of a dictionary.
        for source_key, source_value in source.items():
            if source_key == 'name':
                news_df.loc[article_id, 'source'] = source_value
                
    ## Adding a column to check for data from API that are not full articles. E.g. videos, broadcasts, etc.
    if author == None:
        news_df.loc[article_id,'notArticles'] = True
    else:
        news_df.loc[article_id,'notArticles'] = False

## Changing format of the date and time in the 'publishedAt' column to display date as YYYY-MM-DD and time as Hours:Minutes:Seconds.
news_df['publishedAt'] = pd.to_datetime(news_df['publishedAt']).dt.tz_convert(None)

## Adding five columns to DataFrame. One for day, month, year, full date and time. All taken from 'publishedAt' column.
news_df['day'] = news_df['publishedAt'].dt.day
news_df['month'] = news_df['publishedAt'].dt.month
news_df['year'] = news_df['publishedAt'].dt.year
news_df['date'] = news_df['publishedAt'].dt.date
news_df['time'] = news_df['publishedAt'].dt.time

## Dropping 'content' column because content of article can be accessed via the URL in the 'url' column.
news_df.drop(columns=['content'], inplace = True)

## Creating connection to Pagila database in DBeaver using credentials from '.env' file.
db_conn = psycopg2.connect(database = 'pagila',
                    user = user,
                    password = password,
                    host = host_name,
                    port = 5432
                   )

cursor = db_conn.cursor()

## Executing SQL statement that creates table, if it does not already exist in database, named 'capstone_vg_final'.
cursor.execute("""
        CREATE TABLE IF NOT EXISTS student.capstone_vg_final (
            id INT PRIMARY KEY,
            source VARCHAR(15) NOT NULL,
            author VARCHAR(50) NOT NULL,
            title VARCHAR(100) NOT NULL,
            description VARCHAR(500) NOT NULL,
            url VARCHAR(500) NOT NULL,
            url_to_image VARCHAR(500) NOT NULL,
            published_at TIMESTAMP NOT NULL,
            not_articles BOOLEAN NOT NULL,
            day INT NOT NULL,
            month INT NOT NULL,
            year INT NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL
        );
    """)

## Iterating through rows in 'news_df' DataFrame.
for row in news_df.iterrows():
    ## SQL statement that returns the last used ID from the 'capstone_vg_final' table.
    cursor.execute("""SELECT
                      MAX(id)
                  from
                      student.capstone_vg_final
                """)
    
    ## Fetches the last used ID as a tuple and converts it into an integer.
    last_id = cursor.fetchone()
    last_id = last_id[0]
    ## Checks if the last used ID returned has no value and makes it equal to 0.
    if last_id == None:
        last_id = 0
    
    ## Getting datetime value in 'publishedAt' column from newest row in 'news_df' DataFrame.
    newest_val = max(news_df['publishedAt'])
    ## Getting datetime values in 'publishedAt' column from all rows in 'news_df' DataFrame.
    row_time = row[1][7]
    ## Finding difference between datetime value from newest row and datetime values from all rows in DataFrame.
    diff = newest_val - row_time
    
    ## If the difference is less than or equal to an hour, then execute SQL statement inside if statement code block.
    if diff < pd.Timedelta(1, 'h'):
        
        ## Updates table in database with recent data from DataFrame.
        sql = f"""
            INSERT INTO student.capstone_vg_final(id, source, author, title, description, url, url_to_image, published_at, not_articles, day, month, year, date, time)
            values ({last_id + 1},
                    '{row[1][1]}',
                    '{row[1][2]}',
                    $$'{row[1][3]}'$$,
                    $$'{row[1][4]}'$$,
                    '{row[1][5]}',
                    '{row[1][6]}',
                    '{row[1][7]}',
                    {row[1][8]},
                    {row[1][9]},
                    {row[1][10]},
                    {row[1][11]},
                    '{row[1][12]}',
                    '{row[1][13]}')
            """
        
        cursor.execute(sql)

## Commits updates to table in database and closes connection to database.
db_conn.commit()
db_conn.close()
