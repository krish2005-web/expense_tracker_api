from fastapi import FastAPI,Depends,Request
from app.schemas.user import UserResponse
from app.routers.auth import router as auth_router
from app.routers.expenses import router as expense_router
from app.dependencies import get_current_user
import time
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.exceptions import ExpenseNotFoundException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from app.config import settings
from app.database import Base, engine


app=FastAPI()


@app.on_event("startup")
async def initialize_database():
    if settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        print("SQLite tables ready at startup")

@app.exception_handler(ExpenseNotFoundException)
async def expense_not_found_handler(
    request: Request,
    exc: ExpenseNotFoundException
):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": str(exc)
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    print(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error"
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation failed",
            "details": jsonable_encoder(exc.errors())
        }
    )

app.include_router(auth_router)
app.include_router(expense_router)

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(process_time)

    print(
        f"{request.method} {request.url.path} "
        f"→ {response.status_code} "
        f"→ {process_time:.4f}s"
    )

    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/me",response_model=UserResponse)
def me(current_user = Depends(get_current_user)):
    return current_user

@app.get("/")
def home():
    return {
        "message": "Expense Tracker API is running"
    }

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend",
)

