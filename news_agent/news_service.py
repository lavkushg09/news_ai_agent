import os
import requests
import time
from dotenv import load_dotenv
from datetime import datetime
import logging

logging.basicConfig(
    filename="news_agent.log", 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# Load API key
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY_MEDIA_STACK")

def fetch_top_news(country, category, limit=2):
    url = "http://api.mediastack.com/v1/news"
    params = {
        "access_key": NEWS_API_KEY,
        "countries": country,
        "categories": category,
        "limit": limit,
        "sort": "published_desc",
        "languages": "en"
    }
    logger.info(f"{country=}, {category=}")
    response = requests.get(url, params=params)
    data = response.json()

    if "data" not in data:
        print("Error fetching news:", data)
        return

    return data


