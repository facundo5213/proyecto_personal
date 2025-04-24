from models.base import BaseModel
from typing import List, Optional

    
class MenusInput(BaseModel):
    nombre: str
    descripcion: str
    precio: float