from pydantic import BaseModel
from typing import List


class RestaurantInput(BaseModel):
    _collection_name = "restaurants"

    name: str
    phone: str
    address: str
    comments: str
    #employees: List[dict] = []




