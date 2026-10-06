Expense Tracker - Basic Frontend (No Node.js)

Plain HTML/CSS/JavaScript frontend for the FastAPI Expense Tracker.

Requirements:
- Python 3
- Running FastAPI backend at http://127.0.0.1:8000
- CORS enabled in FastAPI for http://localhost:5500

Run:
1. Open PowerShell in this folder.
2. python -m http.server 5500
3. Open http://localhost:5500

Features:
- Register / Login
- JWT Bearer authentication
- Dashboard summary
- Category summary
- Add expense
- Filter and pagination
- Edit expense (GET + PATCH)
- Delete expense (DELETE)

Backend routes used:
- POST /auth/register
- POST /auth/login
- GET /me
- POST /expense/
- GET /expense/
- GET /expense/{expense_id}
- PATCH /expense/{expense_id}
- DELETE /expense/{expense_id}
- GET /expense/summary
- GET /expense/summary/categories

The frontend stores the JWT access token in localStorage and sends:
Authorization: Bearer <token>
to protected endpoints.
