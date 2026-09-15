import json
import os
import logging

from src.config import REJECTED_FILE_URL


def write_rejected_data(invalid_records):
    if not invalid_records:                 #if no "rejected records", no need to create the file
        logging.info("No rejected records.")
        return
    
    os.makedirs(os.path.dirname(REJECTED_FILE_URL), exist_ok=True)

    with open(REJECTED_FILE_URL,'w' ) as f:
        json.dump(invalid_records,f, indent=4)

    logging.info(f"{len(invalid_records)} rejected records written successfully.")