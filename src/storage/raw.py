import json
import logging

from config import FILE_URL

#Function: insert raw data directly from API into file(products.json)
def write_file(data):
    with open(FILE_URL,'w' ) as f:
        json.dump(data,f, indent=4)

    logging.info("Raw data written into file successfully.")
