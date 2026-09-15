import sqlite3
import copy

from src.storage.database import create_staging_table, load_staging_data
from src.transformation.curated import create_curated_table, transform_staging_to_curated

from src.validation.data_quality import validate_records

#step 1: test load_staging_data
def test_load_staging_data(sample_data, tmp_path):
    test_db_path = tmp_path / "test.db"

    create_staging_table(str(test_db_path))
    #loading data
    load_staging_data(sample_data, str(test_db_path))
   
    connection = sqlite3.connect(test_db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT count(*) FROM stg_products")
    count = cursor.fetchone()[0]

    connection.close()

    assert count == 2

#step 1: test load_staging_data with updates
def test_load_staging_data_updates_existing(sample_data, tmp_path):

    test_db_path = tmp_path / "test.db"

    create_staging_table(str(test_db_path))
    load_staging_data(sample_data, str(test_db_path))

    #modify value in copy of sample_data
    test_data = copy.deepcopy(sample_data)
    test_data[0]["price"] = 250
    #load copy of sample_data
    load_staging_data(test_data, str(test_db_path))

    connection = sqlite3.connect(test_db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT price FROM stg_products WHERE id = 1")
    count = cursor.fetchone()[0]

    connection.close()

    assert count == 250


#step 3: test transform_staging_to_curated(

def test_transform_staging_to_curated(sample_data,tmp_path):
    test_db_path = tmp_path / "test.db"

    # 1. Create and populate staging
    create_staging_table(str(test_db_path))
    load_staging_data(sample_data, str(test_db_path))

    # 2. Create curated table
    create_curated_table(str(test_db_path))

    # 3. Transform staging → curated
    transform_staging_to_curated(str(test_db_path))

    # 4. Verify curated result
    connection = sqlite3.connect(test_db_path)
    cursor = connection.cursor()

    cursor.execute("""SELECT product_id, product_name, category, price, rating
                        FROM dim_product
                        WHERE product_id = 1""")
    row = cursor.fetchone()

    connection.close()

    assert row == (1, "Test Product", "electronics", 100, 4.0)


#step 4: test transform_staging_to_curated with updates
def test_transform_staging_to_curated_updates_existing(sample_data,tmp_path):
    test_db_path = tmp_path / "test.db"

    #original data
    create_staging_table(str(test_db_path))
    load_staging_data(sample_data, str(test_db_path))

    create_curated_table(str(test_db_path))
    transform_staging_to_curated(str(test_db_path))

    #copy of original data
    test_data = copy.deepcopy(sample_data)

    #modify value in copy of original data
    test_data[0]["price"] = 250

    # Reload staging and transform again
    load_staging_data(test_data, str(test_db_path))
    transform_staging_to_curated(str(test_db_path))


    connection = sqlite3.connect(test_db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT price FROM dim_product WHERE product_id = 1")
    row = cursor.fetchone()[0]

    connection.close()

    assert row == 250



#step 5: validate records loaded_to_staging
def test_only_valid_records_loaded_to_staging(sample_data, tmp_path):
    test_db_path = tmp_path / "test.db"

    test_data = copy.deepcopy(sample_data)
    test_data[0]["price"] = -50

    valid_data, invalid_data = validate_records(test_data)

    assert len(valid_data) == 1
    assert len(invalid_data) == 1

    create_staging_table(str(test_db_path))
    load_staging_data(valid_data, str(test_db_path))

    connection = sqlite3.connect(test_db_path)
    cursor = connection.cursor()
  
    cursor.execute("SELECT count(*) FROM stg_products")
    count = cursor.fetchone()[0]

    connection.close()

    assert count == 1


#step 6: validate records loaded_to_curated
def test_valid_data_flows_to_curated(sample_data, tmp_path):

    test_db_path = tmp_path / "test.db"

    test_data = copy.deepcopy(sample_data)
    test_data[0]["price"] = -50

    valid_data, invalid_data = validate_records(test_data)

    assert len(valid_data) == 1
    assert len(invalid_data) == 1

    create_staging_table(str(test_db_path))
    load_staging_data(valid_data, str(test_db_path))

    create_curated_table(str(test_db_path))
    transform_staging_to_curated(str(test_db_path))

    connection = sqlite3.connect(test_db_path)
    cursor = connection.cursor()
  
    cursor.execute("""SELECT product_id, product_name, price, rating
                        FROM dim_product
                        WHERE product_id = 2""")
    row = cursor.fetchone()

    connection.close()

    # assert row == (1, "Test Product", 100, 4.0)
    assert row == (2, "Another Product", 50, 3.5)