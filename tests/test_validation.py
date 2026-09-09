from src.api.client import call_api
from src.validation.data_quality import validate_records


# data = call_api()
# test_data = data.copy()

# test_data[0] = test_data[0].copy()
# test_data[0]["price"] = -50

# valid, invalid = validate_records(test_data)

# print("Valid:", len(valid))
# print("Invalid:", len(invalid))
# print(invalid)


import copy
from src.storage.rejected import write_rejected_data

data = call_api()
test_data = copy.deepcopy(data)

test_data[0]["price"] = -50
test_data[1]["title"] = None

valid, invalid = validate_records(test_data)

print("Valid:", len(valid))
print("Invalid:", len(invalid))

write_rejected_data(invalid)