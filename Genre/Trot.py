import requests
import time
import regex as re  # Using regex package instead of re
import os

from bs4 import BeautifulSoup
from pymongo import MongoClient
from dotenv import load_dotenv

# MongoDB Connection
load_dotenv()
mongo_connection_string = os.getenv('MONGO_CONNECTION_STRING')
mongoClient = MongoClient(mongo_connection_string)

# User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# Connect to MongoDB
mongoCollection = mongoClient['Genre']['Trot']
mongoCollection.delete_many({})

pattern = re.compile(r"[^\p{Hangul}\p{Latin}\p{Nd}\s'\u2019&]+", re.UNICODE)

for i in range(1, 101, 50):
    # URL to scrape
    url = f"https://www.melon.com/genre/song_list.htm?gnrCode=GN0700#params%5BgnrCode%5D=GN0700&params%5BdtlGnrCode%5D=GN0701&params%5BorderBy%5D=NEW&params%5BsteadyYn%5D=N&po=pageObj&startIndex={i}"
    print(url)


    # Request the page
    response = requests.get(url, headers=headers)

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    documents = []

    rank_nodes = soup.select('td > div.wrap.t_center > span.rank')
    title_nodes = soup.select('div.ellipsis.rank01 > span > a')
    singer_nodes = soup.select('div.ellipsis.rank02 > span.checkEllipsis')
    

    for index in range(len(rank_nodes)):
        title_text = title_nodes[index].text
        title_filtered = re.sub(pattern, '', title_text)
        title_filtered = title_filtered.upper().replace('PROD BY', 'PROD').replace('’', "'").strip()

        documents.append({
            'rank': int(rank_nodes[index].text.split('\n')[0]),  # Take the first part of the text, which is the rank
            'title': title_filtered,
            'singer': singer_nodes[index].text,
        })

    # Insert into MongoDB
    mongoCollection.insert_many(documents)