import requests
import logging

from config import API_URL

#Function to call API
def call_api():
    logging.info("Calling API")
    response = requests.get(API_URL, timeout=(5,10))
    response.raise_for_status()
    data=response.json()
    logging.info(f"API call successful. Number of records: {len(data)}")
    return data         