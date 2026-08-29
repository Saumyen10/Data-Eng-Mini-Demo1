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
