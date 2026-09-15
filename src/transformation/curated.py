import sqlite3
import logging

from src.config import DB_URL

#function: Curated Table
def create_curated_table(db_url=DB_URL):
    # connection = sqlite3.connect(DB_URL)
    connection = sqlite3.connect(db_url)
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

#function: transformation: Staging -> Curated
def transform_staging_to_curated(db_url=DB_URL):
    # connection = sqlite3.connect(DB_URL)
    connection = sqlite3.connect(db_url)
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