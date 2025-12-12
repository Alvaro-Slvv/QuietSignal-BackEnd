## Basic instructions
download pfdata.zip, 
add the .env to the project root
and the Model.joblib to root/mlmodel 
> **_NOTE:_** change the .env database credentials  

Run this to install dependencies
```
uv sync
```

Then run this to start the api
```
uv run uvicorn quietsignal_backend.main:app --reload
```

# AUTH ROUTES ***/auth***
|Method | Route | Description |
|-------|-------|-------------|
|POST | /register | Register a new user|
|POST | /login | Login and receive JWT token (includes role) |
|POST | /logout | Logout (frontend token removal) |
|GET | /me | Get current authenticated user |

# USER ROUTES ***/users***
|Method | Route | Description|
|-------|-------|-------------|
|POST | / | Create user (admin-style creation)|
|GET | /me | Get profile of logged-in user|

# JOURNAL ROUTES ***/journals***

|Method | Route | Description|
|-------|-------|-------------|
|GET | /journals/ | List journals belonging to current user|
|POST | /journals/?title=X | Create a new journal|
|-------|-------|-------------|
|POST | /{journal_id}/entries | Create new entry in journal|
|GET | /{journal_id}/entries | List all entries in a journal|
|GET | /{journal_id}/entries/{entry_id} | Get single entry details|
|-------|-------|-------------|
|POS | /journals/{journal_id}/entries/{entry_id}/append | Append a single paragraph to an entry|
|POST | /journals/{journal_id}/entries/{entry_id}/append-batch | Append an array of paragraphs (batch append)|

# AI ANALYSIS ***/analyze***
|Method | Route | Description|
|-------|-------|-------------|
|POST | / | Analyze free text (not tied to journals)|

# ADMIN ROUTES ***/admin***

|Method | Route | Description|
|-------|-------|-------------|
|POST | /recalculate_entries | Recalculate AI emotion predictions for ALL entries|

> [!IMPORTANT]
> Requires user.role == "admin"

# MISC
|Method | Route | Description|
|-------|-------|-------------|
|GET | / | Root health check endpoint|
