from pydantic import BaseModel,EmailStr,ConfigDict
from datetime import date,datetime

class UserCreate(BaseModel):
    name:str
    email:EmailStr
    password:str

class UserResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int
    name:str
    email:EmailStr
    created_at:datetime

class LoginRequest(BaseModel):
    email:EmailStr
    password:str

class LoginResponse(BaseModel):
    access_token:str
    token_type:str
