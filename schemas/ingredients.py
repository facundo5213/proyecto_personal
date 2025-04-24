from models.base import BaseModel
from typing import List, Optional

    
class IngredientsInput(BaseModel):
    name: str
    description: str
    min_stock: int


class IngredientsComplete(BaseModel):

    name: str
    description: str
    restaurant_id :str
    min_stock: int
