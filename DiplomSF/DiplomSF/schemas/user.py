from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=5, max_length=20)
    fam: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=80)
    otc: Optional[str] = Field(None, max_length=80)

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=5, max_length=20)
    fam: Optional[str] = Field(None, min_length=1, max_length=80)
    name: Optional[str] = Field(None, min_length=1, max_length=80)
    otc: Optional[str] = Field(None, max_length=80)

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True