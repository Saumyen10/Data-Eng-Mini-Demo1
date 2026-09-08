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