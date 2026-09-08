from src.api.client import call_api
from src.validation.data_quality import validate_records


data = call_api()
test_data = data.copy()

test_data[0] = test_data[0].copy()
test_data[0]["price"] = -50

valid, invalid = validate_records(test_data)

print("Valid:", len(valid))
print("Invalid:", len(invalid))
print(invalid)

