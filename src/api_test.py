import requests
import json
import logging
import sqlite3

# response = requests.get('https://fakestoreapi.com/products')

# print(response.status_code)
# print(response.text)

# data=response.json()
# data

# print(type(data))       #output = list
# print(len(data))        #output = 20

from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv("API_URL")
FILE_URL = os.getenv("FILE_URL")
DB_URL = os.getenv("DB_URL")


if not API_URL:
    raise ValueError("API_URL is missing or empty in .env")

if not FILE_URL:
    raise ValueError("FILE_URL is missing or empty in .env")


logging.basicConfig(
    level=logging.INFO,         # Capture INFO, WARNING, ERROR, and CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s'
)

#Function to call API
def call_api():
    logging.info("Calling API")
    response = requests.get(API_URL, timeout=(5,10))
    response.raise_for_status()
    data=response.json()
    logging.info(f"API call successful. Number of records: {len(data)}")
    return data         # prints output in json file not in terminal

#Function to write in file
def write_file(data):
    with open(FILE_URL,'w' ) as f:
        json.dump(data,f, indent=4)

    logging.info("Raw data written into file successfully.")
    # print("File write completed successfully.")

    
try:
    data = call_api()
    write_file(data)
    
except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")    


#Function to save data in database
def load_to_database(data):
    connection = sqlite3.connect(DB_URL)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            title TEXT,
            price REAL,
            description TEXT,
            category TEXT
        )
        """
    )
    logging.info("Database table ready.")

    records = [(
                item['id'],
                item['title'],
                item['price'],
                item['description'],
                item['category']
            )
            for item in data
    ]
    cursor.executemany(                                     #INSERT OR IGNORE INTO products
        """
            INSERT INTO products (id,title,price,description,category)  
            VALUES (?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            price = excluded.price,
            description = excluded.description,
            category = excluded.category
        """, 
        records)
    connection.commit()
    logging.info(f"{len(records)} records processed.")
    connection.close()


#call the function
load_to_database(data)