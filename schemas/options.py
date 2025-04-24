from models.base import BaseModel
from typing import List, Optional, Literal

class Component(BaseModel):
    id: str
    unidad: Literal["gr", "ml", "unidad"]
    cantidad: float
    
class Ingredient(BaseModel):
    id: str
    unidad: Literal["gr", "ml", "unidad"]
    cantidad: float


class OptionsInput(BaseModel):
    name: str
    description: str
    type : str
    component: Optional[List[Component]] = None
    ingredient: Optional[List[Ingredient]] = None
    price_modifier : float


class OptionsPatchInput(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    component: Optional[List[Component]] = None
    ingredient: Optional[List[Ingredient]] = None
    price_modifier: Optional[float] = None