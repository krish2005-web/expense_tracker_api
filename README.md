# Expense Tracker API

A full-stack expense management application built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT authentication, and a lightweight HTML/CSS/JavaScript frontend.

## Features

- User registration and login
- Password hashing with pwdlib / Argon2
- JWT-based authentication
- Bearer authentication and protected routes
- User ownership / authorization for expenses
- Expense CRUD operations
- Filtering and pagination
- Overall analytics using SUM, COUNT, and AVG
- Category-wise analytics using GROUP BY
- Pydantic Field validation
- Custom Pydantic field validation
- Centralized configuration with `.env`
- Global exception handling
- Request logging and response timing middleware
- CORS
- Background tasks
- Receipt/image upload with type validation
- Receipt path stored in PostgreSQL
- Alembic migrations
- Frontend for login, dashboard, filtering, add/edit/delete, and summaries

## Tech Stack

### Backend
- Python
- FastAPI
- Pydantic / Pydantic Settings
- SQLAlchemy
- PostgreSQL
- Alembic
- PyJWT
- pwdlib / Argon2
- python-multipart

### Frontend
- HTML
- CSS
- JavaScript
- Fetch API

## Project Structure

```text
expense_tracker_api/
├── app/
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── exceptions.py
│   ├── main.py
│   ├── models/
│   ├── routers/
│   └── schemas/
├── alembic/
├── uploads/
├── tests/
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone

```bash
git clone <your-github-repository-url>
cd expense_tracker_api
```

### 2. Virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Environment variables

Create `.env` from `.env.example`.

Example:

```env
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/expense_tracker
SECRET_KEY=your-secret-key
ALGORITHM=HS256
FRONTEND_URL=http://localhost:5500
```

Do not commit `.env`.

### 5. Run migrations

```powershell
alembic upgrade head
```

### 6. Start the API

```powershell
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Frontend

The current frontend is plain HTML/CSS/JavaScript, so Node.js is not required.

From the frontend directory:

```powershell
python -m http.server 5500
```

Open:

```text
http://localhost:5500
```

The frontend uses Fetch API and Bearer JWT authentication to communicate with FastAPI.

## Database Migrations

Create a migration after changing SQLAlchemy models:

```powershell
alembic revision --autogenerate -m "describe the change"
```

Apply:

```powershell
alembic upgrade head
```

Check current revision:

```powershell
alembic current
```

History:

```powershell
alembic history
```

## Authentication Flow

```text
Register
   ↓
Hash password
   ↓
Store user
   ↓
Login
   ↓
Verify password
   ↓
Issue JWT
   ↓
Authorization: Bearer <token>
   ↓
get_current_user()
   ↓
Protected endpoint
```

## Expense Flow

```text
Frontend / Swagger
       ↓
FastAPI route
       ↓
Pydantic validation
       ↓
Authentication / ownership check
       ↓
SQLAlchemy session
       ↓
PostgreSQL
       ↓
JSON response
```

## Error Handling

Centralized handlers are used for:
- Custom expense-not-found errors
- Request validation errors (`422`)
- Unexpected application errors (`500`)

Example:

```json
{
  "success": false,
  "error": "Validation failed",
  "details": []
}
```

## Security Notes

- Passwords are never stored as plaintext.
- Secrets and database credentials stay in `.env`.
- `.env` is excluded through `.gitignore`.
- Expense queries are scoped to the authenticated user.
- Uploaded receipts are validated by content type.

## Future Improvements

- Automated tests with pytest
- Docker / Docker Compose
- Production deployment
- Refresh tokens / RBAC
- Budget management
- Advanced analytics and charts
- Cloud/object storage for receipts

## Author

**Krishna**

Built as a practical full-stack FastAPI project for learning and portfolio development.


## Render deployment

A simple free-demo deployment can run without a managed PostgreSQL service because the app
falls back to SQLite when `DATABASE_URL` is not provided.

Build command:

```bash
pip install -r requirements.txt && alembic upgrade head
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The repository also includes `render.yaml`. For the free demo deployment, SQLite tables are initialized at application startup.

**Important:** Render Free web services do not provide persistent local filesystem storage,
so the SQLite database and uploaded receipt files are suitable for a demo but not for durable
production data. For a persistent deployment, connect the app to hosted PostgreSQL and set
`DATABASE_URL` in the service environment.

## Render deployment (free demo)

This repository can run a demo without a managed PostgreSQL instance by using SQLite when
`DATABASE_URL` is not configured. The SQLite tables are created during application startup.

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`
- Frontend: served by FastAPI from the `frontend/` directory at `/`
- API docs: `/docs`

**Persistence warning:** a SQLite file and uploaded files on a free web service's local
filesystem are not durable deployment storage. Database data and uploads may disappear on
redeploy/restart. Use a hosted PostgreSQL database for durable data.

For local PostgreSQL development, set `DATABASE_URL` in your `.env` and run
`alembic upgrade head` before starting the app. The no-database SQLite fallback is for demo use.
