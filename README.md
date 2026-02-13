# Yiran-Emily-api

lab 4 project for Advanced Computing.

## Contributors
- Emily Chu
- Yiran Ge


## Connecting to the API
Since we are running our API locally we will access the endpoint at ```http://127.0.0.1:5000``` (or the address the appears on your console).




### 1) List all records
**Endpoint**
- `GET /api/records`

**Example**
```bash
curl "http://127.0.0.1:5000/api/records"
````



### 2) Filter records by any column (exact match)

Any query parameter (except `limit`, `offset`, `format`) is treated as a filter.

**Examples**

```bash
curl "http://127.0.0.1:5000/api/records?county=KINGS"
curl "http://127.0.0.1:5000/api/records?bias_motive_description=ANTI-JEWISH"
```


---

### 3) Pagination (limit & offset)

**Endpoint**

* `GET /api/records?limit=<int>&offset=<int>`

**Example**

```bash
curl "http://127.0.0.1:5000/api/records?limit=108&offset=20"
```

---

### 4) Get a single record by ID

The unique identifier column is `full_complaint_id`.

**Endpoint**

* `GET /api/records/<full_complaint_id>`

**Example**

```bash
curl "http://127.0.0.1:5000/api/records/1234567890"
```

**Not found (404)**

```json
{"error":"Record not found","id":"1234567890"}
```

---

### 5) Output format (JSON or CSV)

**Endpoints**

* `GET /api/records?format=json`
* `GET /api/records?format=csv`

**Examples**

```bash
curl "http://127.0.0.1:5000/api/records?format=json"
curl "http://127.0.0.1:5000/api/records?format=csv"
```

**Combined example**

```bash
curl "http://127.0.0.1:5000/api/records?county=KINGS&limit=50&offset=0&format=csv"
```


