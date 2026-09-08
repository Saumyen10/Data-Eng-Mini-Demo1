import sqlite3
import logging

from src.config import DB_URL

#Function: Staging Table
def create_staging_table():
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



#Function: Load Staging Table
def load_staging_data(data):
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
