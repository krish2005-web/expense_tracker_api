from fastapi import APIRouter,Depends,HTTPException
from app.schemas.user import UserCreate,UserResponse,LoginRequest,LoginResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from pwdlib import PasswordHash
import jwt
from app.config import settings
from datetime import datetime,timezone,timedelta

router=APIRouter(prefix="/auth",
                 tags=["Authentication"])

password_hash=PasswordHash.recommended()


SECRET_KEY=settings.SECRET_KEY
ALGORITHM=settings.ALGORITHM

@router.post("/",status_code=201,response_model=UserResponse)
def register(user:UserCreate,
             db:Session=Depends(get_db)):
    email=db.query(User).filter(User.email==user.email).first()
    if email:
     raise HTTPException(status_code=409,
                        detail="Email already registered")
    new_user=User(
       name=user.name,
       email=user.email,
       password_hash=password_hash.hash(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import (
    UserCreate,
    UserResponse,
    LoginRequest,
    LoginResponse
)
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from pwdlib import PasswordHash

import jwt

from app.config import settings
from datetime import datetime, timedelta, timezone


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

password_hash = PasswordHash.recommended()



SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

if not SECRET_KEY or not ALGORITHM:
    raise ValueError("SECRET_KEY or ALGORITHM is missing in .env")


# ---------------- REGISTER ----------------

@router.post("/register", status_code=201, response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=password_hash.hash(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ---------------- LOGIN ----------------

@router.post("/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_correct = password_hash.verify(
        login_data.password,
        user.password_hash
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
# to_decode=jwt.decode(
#    payload,
#    SECRET_KEY,
#    algorithms=[ALGORITHM]

# return to_encode
   