from src.api.client import call_api
from src.storage.raw import write_file
from src.storage.database import create_staging_table, load_staging_data
from src.transformation.curated import create_curated_table
from src.transformation.curated import transform_staging_to_curated
from src.validation.data_quality import validate_records
from src.storage.rejected import write_rejected_data

import src.logger
import logging
import requests

def main():
    try:
        data = call_api()

        # data[0]["price"] = -50  #testing purposes
        write_file(data)

        valid_data,invalid_data = validate_records(data)
        write_rejected_data(invalid_data)

        create_staging_table()
        load_staging_data(valid_data)
        # load_staging_data(data)
        create_curated_table()
        transform_staging_to_curated()

    except requests.exceptions.RequestException as e:
        logging.error(f"API Error: {e}")


if __name__ == "__main__":
    main()