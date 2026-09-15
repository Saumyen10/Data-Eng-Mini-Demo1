1. Setup initial project directory (files & folders)

---- data-eng
    --- data/
    --- src/
    --- .gitignore
    --- README.md
    --- requirements.txt

2. Setup virtual environment: ( creates .venv folder)

3. Install necessary requirements ( pip install)
    a. python
    b. requests
    c. logging
    d. python-dotenv (for importing environment variables - .env)
    e. sqlite3


4. API call is handle like this

requests.get(URL)
        ↓
HTTP Response
        ↓
response.status_code
        ↓
response.json()
        ↓
Python dictionary/list




--- TASK

Task 1 pipeline:

our Task 1 pipeline is now complete:

Fake Store API
      ↓
 requests.get()
      ↓
 HTTP Response
      ↓
 response.json()
      ↓
 Python list[dict]
      ↓
 json.dump()
      ↓
data/raw/products.json



Task 2 — Make the ingestion reliable

Now we're going to take your working script and make it behave more like an actual data-engineering ingestion program.

Right now, imagine the API goes down.

Your program does:

response = requests.get(...)
data = response.json()

What happens if:

1. API is unavailable?
2. Request takes 5 minutes?
3. API returns 404?
4. API returns 500?
5. Response isn't valid JSON?
6. Internet connection drops?

```
What happens now?

Successful API:

200
 ↓
raise_for_status() → no exception
 ↓
response.json()
 ↓
save products.json
 ↓
File write completed successfully.

API returns 404/500:

raise_for_status()
 ↓
exception
 ↓
except
 ↓
API Error: ...

Connection/read timeout:

requests.get()
 ↓
exception
 ↓
except
 ↓
API Error: ...
```



Logging:


logging.basicConfig(
    # filename='logs/app.log',       ---> optional                       
    # filemode='a',                 ---> optional
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



Format ---

Earlier:

try
 └── call_api()

except
 └── API error

else
 └── write_file()



Now:

try
 └── call_api()
 └── write_file()

except
 └── API error


Flow:

try
 │
 ├── call_api()
 │      │
 │      ├── API request
 │      ├── status check
 │      ├── JSON parsing
 │      └── return data
 │
 └── write_file(data)
        │
        └── save JSON



Task 3: Make the pipeline maintainable

Now we're going to address something you've already started doing intuitively:

Separate responsibilities.


there's still a problem: your code contains the API URL and output path directly inside the functions.

For example:

requests.get('https://fakestoreapi.com/products', ...)


Imagine tomorrow the API changes to:

https://some-other-api.com/products

You'd have to edit your source code.

In real projects, we generally want configuration separated from code.

We will use ENVIRONMENT VARIABLES, so eventually we dont wants any secrets to be hardcoded into the code itself.



Task 3B — Validate the configuration

Before we move toward databases, there's one realistic problem to solve.

Suppose someone accidentally changes .env to:

API_URL=
FILE_URL=data/raw/products.json

or forgets FILE_URL completely.

Your program shouldn't reach the API and fail later in some confusing way. A good pipeline should fail early and clearly.

Your next task is to add configuration validation.

```
Ingestion pipeline now:

             .env
              │
              ▼
      Load configuration
              │
              ▼
       Validate config
              │
         ┌────┴────┐
       FAIL       PASS
         │          │
         ▼          ▼
       Stop       API call
                     │
                     ▼
              Error handling
                     │
                     ▼
                JSON parse
                     │
                     ▼
               Raw JSON file

```


Task 4 — Introduce a database


A JSON file is useful for raw data storage, but imagine we have:

100,000 products
10 million transactions
multiple API responses every day

Now we need to:

query records
filter data
join datasets
aggregate data
enforce structure
update existing records
prevent duplicates

That's where a database becomes much more useful.


The architecture will become:

Fake Store API
       ↓
    Python
       ↓
 products.json       ← raw layer
       ↓
    SQLite DB        ← structured layer
       ↓
      SQL


Now project directory:

mini-data-engineering-project/
│
├── src/
│   └── api_test.py
│
├── data/
│   ├── raw/
│   │   └── products.json
│   └── database/
│       └── products.db
│
├── .env
├── .gitignore
└── README.md


---
UPSERT: not a command in sqlte, combination of INSERT+CONFLICT+UPDATE

| SQL                                    | Meaning                                 |
| -------------------------------------- | --------------------------------------- |
| `INSERT`                               | Insert; duplicate primary key → error   |
| `INSERT OR IGNORE`                     | Insert; duplicate → skip                |
| `INSERT ... ON CONFLICT ... DO UPDATE` | Insert; duplicate → update (**UPSERT**) |


----

Task 5 — Detect INSERT, UPDATE, and UNCHANGED records

difference between full & incremental load

although incremental load is better option, fakestoreapi has fixed dataset, so it never changes. So, ultimately acts like a rigid database.

upsert doesnt verify if "Did the incoming record actually differ from the existing record?"

Create a new function called def process_records(data):
    NEW
     CHANGED
     UNCHANGED


For each item from the API:

Does its ID exist in database?
        │
       NO
        ↓
      NEW
        ↓
     INSERT


       YES
        ↓
Compare:
     title
     price
     description
     category
        │
   ┌────┴────┐
same       different
  ↓            ↓
UNCHANGED    CHANGED
               ↓
             UPDATE

             
Pipeline goal:
                       API
                        ↓
                    call_api()
                        ↓
              ┌─────────┴─────────┐
              ↓                   ↓
        raw JSON file       process_records()
                                  ↓
                     ┌────────────┼────────────┐
                     ↓            ↓            ↓
                   NEW        CHANGED      UNCHANGED
                     ↓            ↓            ↓
                  INSERT        UPDATE       NOTHING
                     └────────────┬────────────┘
                                  ↓
                              SQLite DB



TASK 6: Data Layers

We'll introduce the idea of:
     RAW → STAGING → CURATED

Raw layer: preserve what the source gave you. Principle: Store the source data as close to the original form as practical. 
     e.g. data/raw/products.json

Staging layer: clean, standardize, type-convert, validate. We start making the source data usable.
     e.g. "Electronics" → "electronics"

Curated layer: data shaped for business/analytics use. It is no longer simply "whatever the API sent."
     e.g. "id" → "product_id" 

Right now you have:

API
 ↓
products.json
 ↓
products table

We're going to separate the data into logical layers:

API
 ↓
RAW
 ↓
STAGING
 ↓
CURATED


**Note:** Why not just one table? "Why don't we just clean the API data and put it directly into products?"


Because separating layers gives you:

1. Traceability -
Where did this value come from?
You can trace: Curated → Staging → Raw → API

2. Recovery -

Suppose your transformation code has a bug. You don't necessarily need to call the API again.
You still have: raw/products.json

3. Different consumers

Raw data is useful for engineers.
Staging is useful for transformation.
Curated data is useful for analysts/business users.


---

Create tables:

create_staging_table()
        ↓
load_staging_data()
        ↓
transform_to_curated()

---
New pipeline:

                     API
                      ↓
                   Python
                      ↓
              products.json
                 (RAW)
                      ↓
                stg_products
                (STAGING)
                      ↓
             transform_to_curated()
                      ↓
                dim_product
                (CURATED)


Staging-> Curated:

Transformation logic:
    stg_products
        ↓ SELECT
    (id, title, category, price, rating_rate)
        ↓
    dim_product
    (product_id, product_name, category, price, rating)


Task 7 — Refactor the project

```
Your current project is probably roughly:

mini-data-engineering-project/
│
├── src/
│   └── api_test.py
│
├── data/
│   ├── raw/
│   │   └── products.json
│   └── database/
│       └── products.db
│
├── .env
├── .gitignore
└── README.md
```

And api_test.py contains everything:

configuration
logging
API call
raw-file writing
database creation
staging loading
change detection
curated transformation

That is becoming too much for one file.

```
We want to move toward:

mini-data-engineering-project/
│
├── src/
│   ├── config.py
│   ├── logger.py
│   ├── api/
│   │   └── client.py
│   │
│   ├── storage/
│   │   ├── raw.py
│   │   └── database.py
│   │
│   ├── transformation/
│   │   └── curated.py
│   │
│   └── main.py
│
├── data/
│   ├── raw/
│   │   └── products.json
│   └── database/
│       └── products.db
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md

```


config.py:
     .env
     ↓
     config.py
     ↓
     API_URL / FILE_URL / DB_URL
     ↓
     other modules


Change:

1. process_records() should work with stg_products

Your current process_records() was originally designed around:
     products

Change its target/reference to:
     stg_products


Also remove the function: process_records(data)


So we can simplify the pipeline to:

API
 ↓
call_api()
 ↓
write raw JSON
 ↓
load_staging_data()
     ↓
     INSERT new
     UPDATE existing
 ↓
stg_products
 ↓
transform_staging_to_curated()
 ↓
dim_product


Task 8 — Data Quality & Validation

Our pipeline currently looks like:

API
 ↓
Raw JSON
 ↓
Staging
 ↓
Curated

We're going to make it:

API
 ↓
Raw JSON
 ↓
VALIDATE
 ↓
Staging
 ↓
VALIDATE
 ↓
Curated

The basic principle is:
Don't allow bad data to silently enter the next layer.

Data Quality ----

Data quality is about whether your data is fit for its intended use — accurate, reliable, and trustworthy enough that decisions or downstream systems can depend on it without silently producing wrong results.
A pipeline can run perfectly (no crashes, no exceptions, all your try/except blocks pass) and still produce garbage if the data itself is bad. 

**Note:** This is exactly why "it ran successfully" and "the data is good" are two separate questions.

Dimensions:

For our project, focus mainly on:
     Completeness + Validity + Uniqueness + Consistency.

1. Completeness: Are all the required fields actually present? Missing values, nulls, or empty strings where real data should be.

2. Validity: Does the data conform to expected format, type, or range? A field can be present (satisfying completeness) but still be invalid.

3. Uniqueness: Are there duplicate records that shouldn't exist? PRIMARY KEY constraint is a uniqueness enforcement mechanism.

4. Consistency: Does data agree with itself — across records, across time, or across related tables/sources? This is often the subtlest dimension because each individual value might look "valid" in isolation, but something's contradictory when compared.


Task 8A:  Validate the API response

The responsibility of data_quality.py will be:
     Check whether incoming API records satisfy our basic data-quality rules

Rules: 
     ID, Title, Category, Price, Rating must exist
     Price must be numeric, cannot be negative
     Rating should be valid
     ID must be unique


The function must perform:
        # ID check
        # title check
        # category check
        # price check
        # rating check
        # duplicate check


Now pipeline looks:


              API
               │
               ▼
          call_api()
               │
               ▼
         RAW JSON FILE
               │
               ▼
        validate_records()
          /           \
         /             \
      VALID           INVALID
        │                │
        ▼                ▼
   STAGING DB       REJECTED JSON
        │
        ▼
     CURATED


Task 8B — Integrate validation into the pipeline + quarantine invalid records.


The important design decision is:
     Save raw data first, validate second.

So even invalid data remains available in the raw snapshot for debugging.

---- 

We don't want:

API
 ↓
STAGING
 ↓
VALIDATION

because bad records have already entered our staging layer.

We want:

API
 ↓
RAW
 ↓
VALIDATION
 ↓
only valid data → STAGING


for testing purposes, in main.py added:
       data = call_api()

        data[0]["price"] = -50  #testing purposes
        write_file(data)

which lead to: 19 files in both tables of products.db & products.json

1 file in raw/invalid_products.json:

[
    {
        "record": {
            "id": 1,
            "title": "Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops",
            "price": -50,
            "description": "Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve, your everyday",
            "category": "men's clothing",
            "image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_t.png",
            "rating": {
                "rate": 3.9,
                "count": 120
            }
        },
        "errors": [
            "Invalid price: Negative"
        ]
    }
]

Now, will remove the testing part, but will keep: invalid_products.json as learning purposes



Task 9: Automated Testing


We now want the computer to verify the behavior for us.

The goal is:

Code changes
     ↓
Run tests
     ↓
PASS / FAIL

     rather than manually checking:

"Did it insert 20?"
"Did the invalid record get rejected?"
"Did the database update correctly?"


Why automated testing, conceptually

Everything you've done so far — printing counts, eyeballing output, manually forcing a 404, manually corrupting a record to test validation — has been manual verification. It works, but you have to remember to do it, you do it once, and nothing stops a future code change from silently breaking something you already fixed. Automated tests turn those manual checks into code that runs itself, repeatedly, forever, and tells you immediately if something breaks.


Task 9A — Test validate_records()

Create something conceptually like:

def test_valid_records():
    ...

The test should:

Get your normal API data or use a small test dataset.
Call:
validate_records(data)
Assert:
20 valid
0 invalid

Instead of:

print(...)

you'll do something like:

assert len(valid) == 20
assert len(invalid) == 0


Eventually you have to create these functions:
     test_valid_records
     test_negative_price
     test_missing_title
     test_invalid_rating


You asked:

"So, we will be calling API for every individual function separately?"

For your current version, yes. But I don't recommend keeping it that way.

Imagine you eventually have 50 tests.

Your test suite would do:

Test 1 → API call
Test 2 → API call
Test 3 → API call
...
Test 50 → API call

That's undesirable because:

it's slower
it depends on internet/API availability
the API data could change
the API could rate-limit you
a failing API can make unrelated tests fail

This is exactly why we said earlier:

Automated tests should generally not depend on live external systems.

Better approach

Create a small fixed test dataset inside your tests. e. sample_data = []


Then:

test_valid_records
    ↓
sample_data

test_negative_price
    ↓
deepcopy(sample_data)
    ↓
modify price

test_missing_title
    ↓
deepcopy(sample_data)
    ↓
modify title

test_invalid_rating
    ↓
deepcopy(sample_data)
    ↓
modify rating


Now your tests are:

     fast
     repeatable
     offline
     predictable


Task 9B — Pytest fixtures

Now we'll improve the tests rather than immediately adding more.

You currently repeat this dataset setup conceptually across the tests:

test_data = copy.deepcopy(sample_data)

Pytest fixtures let us define reusable test data/setup once and inject it into tests.

 Create tests/conftest.py:

     move the sample_data code to conftest.py & create a fixture -

     import pytest


@pytest.fixture
def sample_data():
    return [ {}, {}  ]


Task 9C: all validation tests

1. Missing ID
2. Duplicate ID
3. Missing category
4. Missing price
5. Non-numeric price
6. Missing rating
7. Non-numeric rating


Task 9D: Database Integration Test

D.1:
Changed required functions to following format - 

```
def create_curated_table(db_url=DB_URL):
    # connection = sqlite3.connect(DB_URL)
    connection = sqlite3.connect(db_url)
```


def create_staging_table(db_url=DB_URL):
    ...

def load_staging_data(data, db_url=DB_URL):
    ...

def create_curated_table(db_url=DB_URL):
    ...

def transform_staging_to_curated(db_url=DB_URL):
    ...

For the functions that receive data, keep data first and db_url second. That gives us clean calls such as:

     load_staging_data(sample_data, str(test_db))


What this test does:

sample_data
    ↓
temporary test.db
    ↓
create stg_products
    ↓
load_staging_data()
    ↓
SELECT COUNT(*)
    ↓
assert 2

Your actual:

     data/database/products.db

is never touched.


Task 9D.2 — Test the curated transformation

We want to automatically verify that your transformation logic works.

Test 1 — Staging records become curated records

Create another test in tests/test_database.py:

def test_transform_staging_to_curated(sample_data, tmp_path):
    ...

The flow should be:

temporary DB
      ↓
create staging table
      ↓
load sample_data
      ↓
create curated table
      ↓
transform staging → curated
      ↓
SELECT from dim_product
      ↓
assert results



Task 9A — Validation unit tests        ✅
Task 9B — Staging integration tests   ✅
Task 9C — Curated integration tests   ✅
Task 9D — Validation → curated flow   ✅