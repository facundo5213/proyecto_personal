from pydantic import BaseModel, EmailStr
from typing import List, Optional, Literal
from datetime import datetime


# Agrupación de artículos individuales. Cada uno con su precio.
class IndividualItem(BaseModel):
    final_article_id: str
    options: Optional[List[str]] = None # Lista de id's de las opciones elegidas
    quantity: float = 1.00
    status: Literal["pending", "preparing", "ready", "delivered", "cancelled"] = "pending"

class MenuItemComplete(IndividualItem):
    price: float

# Agrupación de artículos bajo un menú promocional con un precio de conjunto
class MenuGroup(BaseModel):
    menu_id: str  # ID del menú promocional
    items: List[IndividualItem]  # Artículos que forman parte del menú

class MenuGroupComplete(MenuGroup):
    price: float  # Precio fijo del menú


class OrdersInput(BaseModel):
    #user_id: PyObjectId
    #restaurant_id: str
    table_id: Optional[str] = None
    menu_items: Optional[List[IndividualItem]] = None # Final Articles individuales
    menu_groups: Optional[List[MenuGroup]] = None  # Menús promocionales (p. ej., menú ejecutivo/daily_menu)
    assigned_employee: str
    closed_order_at: Optional[datetime] = None
    comments: Optional[str] = None
    status: Literal["open", "cancelled", "closed"] = "open"
    order_type: Literal["dine_in", "takeaway", "delivery"] = "dine_in"

    class Config:
        allow_mutation = True 

class OrdersInputComplete(OrdersInput):
    restaurant_id: str
    menu_items: Optional[List[MenuItemComplete]] = None  # Enriquecido con precio y estado
    menu_groups: Optional[List[MenuGroupComplete]] = None  # Menús promocionales (p. ej., menú ejecutivo)
    amount: float


