import os
from datetime import datetime
from pathlib import Path 

# Google cloud storage information / service key
GS_BUCKET = os.environ["GS_BUCKET_NAME"]
GS_PROJECT_ID = os.environ["GS_PROJECT_ID"]
GS_SERVICE_KEY = os.environ["GS_SERVICE_KEY"]

# Pinecone database information / API key
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
PINECONE_UPSERT_BATCH = 100

# OpenAI API key / model info
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = "text-embedding-ada-002"
OPENAI_EMBEDDING_BATCH = 100

# Aiflow job parameters
AIRFLOW_DAG_ID = "trip-advisor-web-scraper"
AIRFLOW_START_DATE = datetime(2023, 5, 8, 8, 0, )
AIRFLOW_SCHEDULE = "*/5 * * * *"
AIRFLOW_CITIES_PER_JOB = 2

# TripAdvisor event processing parameters
TRIPADVISOR_API_URL = "https://www.tripadvisor.com/data/graphql/ids"
MIN_DISTANCE = 50  # Min distance when finding a cities tripadviser id (km)
DEFAULT_DURATION = 45  # Default activity duration if non provided (mins)
DEFAULT_RATING = 2.5  # Default activity rating if non provided (out of 5)
DEFAULT_REVIEW_COUNT = 0 # Default activity review count if non provided

# Internal path strings (DO NOT CHANGE)
BASE_FILEPATH = Path(__file__).resolve().parent
CACHE_FILENAME = "cache/city_cache.json"
REQUEST_ATTR_ID_JSON = "scraper/api_requests/attraction_id.json"
REQUEST_ATTR_DETAILS_JSON = "scraper/api_requests/attraction_detail.json"
REQUEST_CITY_ID_JSON = "scraper/api_requests/city_id.json"
REQUEST_HEADER_JSON = "scraper/api_requests/headers.json"