from models.base import Base
from typing import List, Optional, Literal
from datetime import datetime


class OrdersModel(Base):
    _collection_name = "orders"

    #user_id: PyObjectId
    restaurant_id: str
    table_id: Optional[str] = None
    menu_items: List[dict] = []
    """                 Ejemplo: [  {"final_article_id": "item1", "quantity": 2, "status": "", "options": [], "price": 10.00},
                                    {"final_article_id": "item2", "quantity": 1, "status": "", "options": [], "price": 5.99}]
    """
    menu_groups: List[dict] = [] # Ej: {"menu_id": str", "items": {menu_items}, "price": 20.00}
    assigned_employee: str
    closed_order_at: Optional[datetime] = None # ¿La duración de la mesa ocupada (del pedido) sería desde que la mesa es ocupada
    # o el pedido recibido y generado por el mozo, hasta que el pedido es abonado o la mesa liberada?
    # Podríamos guiarnos con las cámaras de IA para captar el momento en que una es ocupada y liberada
    comments: Optional[str] = None
    amount: float
    status: Literal["open", "cancelled", "closed"] = "open"
    order_type: Literal["dine_in", "takeaway", "delivery"] = "dine_in"



"""
Hasta el momento están hechas las validaciones de table_id y menu_items (puede ser None)
restaurant_id se asigna automáticamente según el admin logueado
(por el momento solo en el create. ### Agregar al update ###)

########## FALTA:

Validar el assigned_employee
(habría que poner una dependencia para usar los endpoints de orden con un "get_employee_current" para registrar
que empleado crea, modifica o elimina una orden)
#### Lo maneja el front. Modificar employeeModelLogin

Hacer suma de los precios de cada menu_item y que se refleje en "amount"
(HECHO. Funciona bien pero los final_articles que se agregan a un menu_group no se validan dentro del menu_group (daily_menu)
Tengo que validar los artículos dentro del menu por su id y sino que devuelva que no existe.)

¿Deberíamos sacar el "amount" del Input?     ### SI ###
¿Deberíamos sacar el price de cada menu_item individual en orders?




Crear las funciones necesarias para disminuir automáticamente el stock cuando se realiza un pedido. 
(Pensarlo y hablar con Joe)

Manejar operaciones como transacciones en MongoDB (usando session) para garantizar consistencia en la disminución del inventario.
(Investigarlo bien)

Documentar casos específicos como productos agotados o pedidos incompletos.
(Pensar que va a depender de "Stock", como un trigger para productos agotados)

"""
