from models.base import BaseModel
from typing import List, Optional

    
class RoomsInput(BaseModel):
    room_number: int  
    description: str
    #tables: List[dict] = [] 
    restaurant_id: str