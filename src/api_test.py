import requests
import json
import logging

# response = requests.get('https://fakestoreapi.com/products')

# print(response.status_code)
# print(response.text)

# data=response.json()
# data

# print(type(data))       #output = list
# print(len(data))        #output = 20


logging.basicConfig(
    level=logging.INFO,         # Capture INFO, WARNING, ERROR, and CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def call_api():
    logging.info("Calling API")
    response = requests.get('https://fakestoreapi.com/products', timeout=(3,5))
    response.raise_for_status()
    data=response.json()
    logging.info(f"API call successful. Number of records: {len(data)}")
    return data         # prints output in json file not in terminal


def write_file(data):
    with open('data/raw/products.json','w' ) as f:
        json.dump(data,f, indent=4)

    logging.info("Raw data written into file successfully.")
    # print("File write completed successfully.")

    
try:
    data = call_api()
    write_file(data)
    
except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")    
