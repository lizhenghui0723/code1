from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int

class ProductUpdate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    user_id: int
    class Config:
        orm_mode = True

class StockChange(BaseModel):
    product_id: int
    change: int
    type: str

class StockLogOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    change: int
    type: str
    timestamp: datetime
    class Config:
        orm_mode = True 