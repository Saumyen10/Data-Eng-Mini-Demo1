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

    # records = [(
    #             item['id'],
    #             item['title'],
    #             item['price'],
    #             item['description'],              #Upsert logic no longer required so commented out the logic
    #             item['category']
    #         )
    #         for item in data
    # ]

    # cursor.executemany(                                     #INSERT OR IGNORE INTO products
    #     """
    #         INSERT INTO products (id,title,price,description,category)  
    #         VALUES (?,?,?,?,?)
    #         ON CONFLICT(id) DO UPDATE SET
    #         title = excluded.title,
    #         price = excluded.price,
    #         description = excluded.description,
    #         category = excluded.category
    #     """, 
    #     records)
    connection.commit()
    # logging.info(f"{len(records)} records processed.")
    connection.close()


#call the function
# load_to_database(data)


#teporarily changing value to test
# data[0]['price'] = data[0]['price'] + 10

#function
def process_records(data):
    connection = sqlite3.connect(DB_URL)
    cursor = connection.cursor()

    inserted=0
    updated=0
    unchanged=0

    
    for item in data:

        cursor.execute(
        "SELECT title, price, description, category FROM products WHERE id = ?",
            (item['id'],)
            )
        existing = cursor.fetchone()
        new_values = (item['title'], item['price'], item['description'], item['category'])

        if existing is None:
            insert_values = (item['id'], item['title'], item['price'], item['description'], item['category'])
            cursor.execute(
            """
            INSERT INTO products (id,title,price,description,category)  
            VALUES (?,?,?,?,?)
            """, insert_values)
            inserted+=1
        elif existing != new_values:
            update_values = (item['title'], item['price'], item['description'], item['category'], item['id'])
            cursor.execute(
            """
            UPDATE products  
            SET title=?, price=?, description=?, category=? where id=?
            """, update_values)
            updated+=1
        else:
            unchanged+=1

    connection.commit()
    logging.info(f"Inserted: {inserted}")
    logging.info(f"Updated {updated}")
    logging.info(f"Unchanged {unchanged}")
    connection.close()


#function call
# process_records(data)


#Task 6: Staging table

def create_stagingtable():
    connection = sqlite3.connect(DB_URL)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stg_products (
           id INTEGER PRIMARY KEY,
            title TEXT,
            price REAL,
            description TEXT,
            category TEXT,
            image TEXT,
            rating_rate REAL,
            rating_count INTEGER
        )
        """
    )
    logging.info("Staging table ready.")
    connection.commit()
    connection.close()

#Staging Load function
def load_stagingdata(data):
    connection = sqlite3.connect(DB_URL)
    cursor = connection.cursor()
    records = [(
                item['id'],
                item['title'],
                item['price'],
                item['description'],              
                item['category'],
                item['image'],
                item['rating']['rate'],     #since nested in rating
                # item['rating']['count']
                # item.get('rating', {}).get('rate')    #another  way to do it
                item.get('rating', {}).get('count')
                
            )
            for item in data
    ]
    logging.info(f"Records prepared for staging: {len(records)}")
    cursor.executemany(                                  
        """
            INSERT INTO stg_products (id,title,price,description,category,image,rating_rate,rating_count)  
            VALUES (?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            price = excluded.price,
            description = excluded.description,
            category = excluded.category,
            image = excluded.image,
            rating_rate = excluded.rating_rate,
            rating_count = excluded.rating_count
        """, 
        records)
    connection.commit()
    logging.info("Staging data loaded successfully.")
    connection.close()


create_stagingtable()
load_stagingdata(data)


# connection = sqlite3.connect(DB_URL)
# cursor = connection.cursor()

# cursor.execute("SELECT COUNT(*) FROM stg_products")
# count = cursor.fetchone()[0]

# print("Rows in stg_products:", count)

# connection.close()


#function: Curated Table
def create_curatedtable():
    connection = sqlite3.connect(DB_URL)
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS dim_product (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            price REAL,
            rating REAL
        )
        """
    )
    logging.info("Curated table ready.")
    connection.commit()
    connection.close()


create_curatedtable()

#transformation: Staging -> Curated
def transform_staging_to_curated():
    connection = sqlite3.connect(DB_URL)
    cursor = connection.cursor()

    cursor.execute(
    "SELECT id, title, category, price, rating_rate FROM stg_products"
    )
    staged_data = cursor.fetchall()
    
    logging.info(f"Records prepared for curated table: {len(staged_data)}")
    cursor.executemany(                                  
        """
            INSERT INTO dim_product (product_id,product_name,category,price,rating)  
            VALUES (?,?,?,?,?)
            ON CONFLICT(product_id) DO UPDATE SET
            product_name = excluded.product_name,
            category = excluded.category,
            price = excluded.price,
            rating = excluded.rating
        """, 
        staged_data)
    connection.commit()
    logging.info("Curated data loaded successfully.")
    connection.close()

transform_staging_to_curated()