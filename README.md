# Description
QuietSignal is a FastAPI-powered mental-wellbeing backend that lets users create journals, store entries, and analyze their emotional content using a machine-learning model.
It provides secure authentication, role-based access control, and an AI-driven sentiment engine for multi-paragraph analysis.
Designed for simplicity and reliability, QuietSignal offers clean endpoints for journaling workflows, user management, and admin maintenance tasks.

# Environment Requirements
QuietSignal runs in a lightweight, modern Python environment and supports all major operating systems.

***Operating System:*** Windows 10/11  

***Programming Language:*** Python 3.10 – 3.12 (recommended: Python 3.11)  

***Package & Environment Management:*** uv  

**Database:** MySQL 8.0+ (local or cloud)  

**Model File**  
> [!IMPORTANT]
>Requires the ML model file at:
>mlmodel/Model.joblib  

# Installation

Follow these steps to set up the QuietSignal backend environment.  

1. Clone the repositor
``` powershell
git clone https://github.com/your-username/QuietSignal-BackEnd.git
cd QuietSignal-BackEnd
```
2. Sync the dependencies and create the virtual enviorment
``` powershell
uv sync
```
3. Prepare enviorment variables (if hosting in local)
``` powershell
# this is an example .env
# JWT
JWT_SECRET_KEY=JWTSECRETKEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# MySQL
MYSQL_USER=USER
MYSQL_PASSWORD=PASSWORD
MYSQL_HOST=HOST
MYSQL_PORT=PORT
MYSQL_DB=quietsignal

ADMIN_EMAIL=ADMIN@ADMIN.com
ADMIN_PASSWORD=ADMINPASSWORD
ADMIN_NAME="ADMIN"
```
# Run Instructions
run the following
``` powershell
uv run uvicorn quietsignal_backend.main:app --reload
```

# API ROUTES
## AUTH ROUTES ***/auth***
|Method | Route | Description |
|-------|-------|-------------|
|POST | /register | Register a new user|
|POST | /login | Login and receive JWT token (includes role) |
|POST | /logout | Logout (frontend token removal) |
|GET | /me | Get current authenticated user |

## USER ROUTES ***/users***
|Method | Route | Description|
|-------|-------|-------------|
|POST | / | Create user (admin-style creation)|
|GET | /me | Get profile of logged-in user|

## JOURNAL ROUTES ***/journals***

|Method | Route | Description|
|-------|-------|-------------|
|GET | / | List journals belonging to current user|
|POST | /?title=X | Create a new journal|
|-------|-------|-------------|
|POST | /{journal_id}/entries | Create new entry in journal|
|GET | /{journal_id}/entries | List all entries in a journal|
|GET | /{journal_id}/entries/{entry_id} | Get single entry details|
|-------|-------|-------------|
|POST | /journals/{journal_id}/entries/{entry_id}/append | Append a single paragraph to an entry|
|POST | /journals/{journal_id}/entries/{entry_id}/append-batch | Append an array of paragraphs (batch append)|

## AI ANALYSIS ***/analyze***
|Method | Route | Description|
|-------|-------|-------------|
|POST | / | Analyze free text (not tied to journals)|

## ADMIN ROUTES ***/admin***

|Method | Route | Description|
|-------|-------|-------------|
|POST | /recalculate_entries | Recalculate AI emotion predictions for ALL entries|

> [!IMPORTANT]
> Requires user.role == "admin"

## MISC
|Method | Route | Description|
|-------|-------|-------------|
|GET | / | Root health check endpoint|



