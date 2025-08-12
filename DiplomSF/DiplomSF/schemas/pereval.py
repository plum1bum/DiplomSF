from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class Coords(BaseModel):
    latitude: float = Field(..., gt=-90, lt=90)
    longitude: float = Field(..., gt=-180, lt=180)
    height: int

class Image(BaseModel):
    img: str  # base64 encoded image
    title: str

class User(BaseModel):
    email: EmailStr
    phone: str
    fam: str
    name: str
    otc: Optional[str] = None

class PerevalInput(BaseModel):
    beauty_title: Optional[str] = None
    title: str
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    add_time: Optional[str] = None
    coords: Coords
    user: User
    images: List[Image]

class PerevalResponse(PerevalInput):
    id: int
    status: str