from pydantic import BaseModel, EmailStr


class AdminRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class AdminLogin(BaseModel):
    email: EmailStr
    password: str