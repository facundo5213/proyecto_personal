from models.base import BaseModel as BaseModelComplete
from typing import List, Optional
from pydantic import BaseModel


class GeneralMenuInput(BaseModelComplete):
    #restaurant_id :str
    name :str
    description:str
    final_articles : Optional[List[str]] = None
    daily_menu : Optional[List[str]] = None
    class Config:
        allow_mutation = True 


class GeneralMenuInputComplet(BaseModelComplete):
    restaurant_id :str
    name :str
    description:str
    final_articles : Optional[List[str]] = None
    daily_menu : Optional[List[str]] = None


class Options(BaseModel):
    id: str
    display_name: str
    unit : str
    quantity : float
    price : float

class Article(BaseModelComplete):
    id: str
    name: str
    description: str
    options: List[Options]
    price: float


class FinalArticleCategory(BaseModel):
    id: str
    name: str
    articles: List[Article]

class MenuResponse(BaseModelComplete):
    restaurant_id: str
    name: str
    description: str
    final_articles: List[FinalArticleCategory]  # Cambiar para reflejar la estructura actual
    daily_menu: List
    

