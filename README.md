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