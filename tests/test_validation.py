# from src.api.client import call_api
# from src.validation.data_quality import validate_records


# data = call_api()
# test_data = data.copy()

# test_data[0] = test_data[0].copy()
# test_data[0]["price"] = -50

# valid, invalid = validate_records(test_data)

# print("Valid:", len(valid))
# print("Invalid:", len(invalid))
# print(invalid)


# import copy
# from src.storage.rejected import write_rejected_data

# data = call_api()
# test_data = copy.deepcopy(data)

# test_data[0]["price"] = -50
# test_data[1]["title"] = None

# valid, invalid = validate_records(test_data)

# print("Valid:", len(valid))
# print("Invalid:", len(invalid))

# write_rejected_data(invalid)


# from src.api.client import call_api                 #not required
from src.validation.data_quality import validate_records

import copy

#move sample_data to conftest.py(fixture)
# sample_data = [
   
# ]


def test_valid_records(sample_data):
#    data = call_api()
    valid, invalid = validate_records(sample_data)

    assert len(valid) == 2
    assert len(invalid) == 0


def test_negative_price(sample_data):
    
    test_data = copy.deepcopy(sample_data)
    test_data[0]["price"] = -50
    valid, invalid = validate_records(test_data)

    assert len(valid) == 1
    assert len(invalid) == 1
    assert "Invalid price: Negative" in invalid[0]["errors"]

def test_missing_title(sample_data): 
    
    test_data = copy.deepcopy(sample_data)
    test_data[0]["title"] = None
    valid, invalid = validate_records(test_data)

    assert len(valid) == 1
    assert len(invalid) == 1
    assert "Missing Title" in invalid[0]["errors"]

def test_invalid_rating(sample_data):
    
    test_data = copy.deepcopy(sample_data)
    test_data[0]["rating"]["rate"] = 6.5
    valid, invalid = validate_records(test_data)

    assert len(valid) == 1
    assert len(invalid) == 1
    assert "Invalid rating: out of Range" in invalid[0]["errors"]

def test_duplicate_id(sample_data):
    test_data = copy.deepcopy(sample_data)
    test_data[1]["id"] = test_data[0]["id"]

    valid, invalid = validate_records(test_data)

    assert len(valid) == 1
    assert len(invalid) == 1
    assert "Duplicate ID" in invalid[0]["errors"]

def test_missing_price(sample_data):

    test_data = copy.deepcopy(sample_data)
    test_data[0]["price"] = None
    valid, invalid = validate_records(test_data)

    assert len(valid) == 1
    assert len(invalid) == 1
    assert "Invalid price: Missing" in invalid[0]["errors"]

def test_non_numeric_price(sample_data):

    test_data = copy.deepcopy(sample_data)
    test_data[0]["price"] = "ABC"
    valid, invalid = validate_records(test_data)

    assert len(valid) == 1
    assert len(invalid) == 1
    assert "Invalid price: not Numeric" in invalid[0]["errors"]

def test_missing_category(sample_data):

    test_data = copy.deepcopy(sample_data)
    test_data[0]["category"] = None
    valid, invalid = validate_records(test_data)

    assert len(valid) == 1
    assert len(invalid) == 1
    assert "Missing Category" in invalid[0]["errors"]
    
def test_missing_rating(sample_data):

    test_data = copy.deepcopy(sample_data)
    test_data[0]["rating"]["rate"] = None
    valid, invalid = validate_records(test_data)

    assert len(valid) == 1
    assert len(invalid) == 1
    assert "Invalid rating: Missing" in invalid[0]["errors"]

def test_non_numeric_rating(sample_data):

    test_data = copy.deepcopy(sample_data)
    test_data[0]["rating"]["rate"] = "xyz"
    valid, invalid = validate_records(test_data)

    assert len(valid) == 1
    assert len(invalid) == 1
    assert "Invalid rating: not Numeric" in invalid[0]["errors"]

def test_missing_id(sample_data):

    test_data = copy.deepcopy(sample_data)
    test_data[0]["id"] = None
    valid, invalid = validate_records(test_data)

    assert len(valid) == 1
    assert len(invalid) == 1
    assert "Missing ID" in invalid[0]["errors"]