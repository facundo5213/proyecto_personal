from models.base import BaseModel
from typing import List, Optional, Literal

class TablesInput(BaseModel):
    table_number: str
    capacity: int
    status: Literal["free", "occupied", "blocked"] = "free"
    orders: List[dict] = [] 
    assigned_employee : str
    room_id: str
    #assigned_at: str
    x : float
    y : float
    type : str


class TablesUpdateInput(BaseModel):
    table_number: Optional[str] = None
    capacity: Optional[int] = None
    status: Literal["free", "occupied", "blocked"] = None
    orders: List[dict] = []
    assigned_employee : Optional[str] = None
    room_id: Optional[str] = None
    #assigned_at: Optional[str] = None
    x : float = None
    y : float = None
    type : Literal["table_circle_small", 
                   "table_circle", 
                   "table_rectangle",
                   "table_small",
                   "table_oval_xl",
                   "table_oval_s",
                   ] = None


class AssignInput(BaseModel):
    identifier: int  