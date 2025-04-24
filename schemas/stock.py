from models.base import BaseModel
from typing import List, Optional

class StockInput(BaseModel):
    restaurant_id: str
    ingredient_id: str
    quantity: str 
    unit: float
    minimum_threshold: int 
    min_stock: int 
    unit_price: float
    vendor: str
    last_updated: str

class StockUpdateInput(BaseModel):
    unit_price: Optional[float] = None
    status: Optional[str] = None
    vendor : Optional[str] = None
    