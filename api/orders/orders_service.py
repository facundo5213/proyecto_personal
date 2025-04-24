from motor.motor_asyncio import AsyncIOMotorDatabase
from utils.presentation.errors import NotFoundException
from models.orders import OrdersModel
from repositories.orders import OrdersRepository
from schemas.orders import OrdersInput, OrdersInputComplete
from utils.presentation.response import ApiResponse


class OrdersService:
    def __init__(self, api_response: ApiResponse, main_db: AsyncIOMotorDatabase):
        self.api_response = api_response
        self.main_db = main_db
        self.orders_repository = OrdersRepository(self.main_db)

    async def add_order(self, orders_input: OrdersInput, restaurant_id) -> OrdersModel:
        self.api_response.logger.info(f"Create order_db in db.")

        # # Valido la existencia del Restaurant asignado
        # existing_restaurant = await self.main_db.restaurants.find_one({"_id": orders_input.restaurant_id})
        # if not existing_restaurant:
        #     raise NotFoundException("Invalid restaurant_id")

        # Valido la existencia de la Table asignada
        if orders_input.table_id != None:
            existing_table = await self.main_db.tables.find_one({"_id": orders_input.table_id})
            if not existing_table:
                raise NotFoundException("Invalid table_id")
            
        # Valido la existencia de los Final Articles asignadas en menu_items
        for item in orders_input.menu_items:
            existing_item = await self.main_db.final_articles.find_one({"_id": item.final_article_id})
            if not existing_item:
                raise NotFoundException(f"The final_articles's id <{item.final_article_id}> is invalid")
            
        # Valido la existencia de los menu_id
        for menu_special in orders_input.menu_groups:
            existing_item = await self.main_db.daily_menu.find_one({"_id": menu_special.menu_id})
            if not existing_item:
                raise NotFoundException(f"The menu's id <{menu_special.menu_id}> is invalid")
            
        
        # Rastreo los precios de los menu_items y sus options
        input_data = orders_input.model_dump()  # Primero convertimos el modelo en un diccionario

        parcial_price = 0.00  # Inicializamos el precio parcial

        # Iteramos sobre los items de menú_items (final_articles)
        for item in input_data["menu_items"]:
            final_article = await self.main_db.final_articles.find_one({"_id": item["final_article_id"]})
            
            # Agregamos la variable del precio a cada item de menu_items
            item["price"] = final_article["price"]  # Agregamos el precio al item en el diccionario
            
            # Validar y sumar los precios de las opciones seleccionadas
            for option_id in item["options"]:
                option = None
                for opt in final_article["options"]:
                    if opt["id"] == option_id:
                        option = opt
                        break
                if not option:
                    raise NotFoundException(f"Option id <{option_id}> is invalid for final_article <{item.final_article_id}>")
                
                item["price"] += option["modificador_precio"]  # Sumamos al precio del final_article cada una de las opciones
            
            # Acumulamos el precio de cada uno de los final_articles con sus opciones y cantidades
            parcial_price += item["price"] * item["quantity"]


        # Rastreo los precios de los menu_groups
        # Iteramos sobre los items de menú (FALTA validar que los final_articles realmente estén agregados al menu_group,
        # por el momento solo se valida el id del menu_group(daily_menu) y se buscan los precios en final_articles directamente)
        for menu_group in input_data["menu_groups"]:
            menu = await self.main_db.daily_menu.find_one({"_id": menu_group["menu_id"]})
            # Agregamos la variable del precio a cada menu_group
            menu_group["price"] = menu["special_price"]

            # Acumulamos el precio de cada uno de los menu_groups
            parcial_price += menu_group["price"]



        # Creamos la variable amount y le asignamos el precio acumulado de los menu_items y menu_groups
        input_data["amount"] = parcial_price

        # # Modelamos el objeto para agregarle los datos necesarios (restaurant_id, precios)
        # input_data = orders_input.model_dump()  # Usamos model_dump() aquí en lugar de dict()
        input_data["restaurant_id"] = restaurant_id 
        input_model = OrdersInputComplete.model_validate(input_data)

        order_db = await self.orders_repository.create(input_model)
        self.api_response.logger.info(f"order_db: {order_db}")
        return order_db

    async def get_orders(self) -> list[OrdersModel]:
        self.api_response.logger.info("Init get orders from db.")
        orders_db = await self.orders_repository.get_all_actives()
        self.api_response.logger.info(f"orders_db: {orders_db}")
        return orders_db

    async def get_order_by_id(self, order_id: str) -> OrdersModel:
        self.api_response.logger.info(f"Init get order from db, order_id: {order_id}")
        order_db = await self.orders_repository.get_active_by_id(order_id)
        self.api_response.logger.info(f"order_db: {order_db}")
        return order_db

    async def change_order(self, order_id: str, modify_orders_input: OrdersInput) -> OrdersModel:
        self.api_response.logger.info(f"Get order from db, order_id: {order_id}")
        order_db = await self.orders_repository.get_active_by_id(order_id)
        self.api_response.logger.info(f"order_db: {order_db}")
        self.api_response.logger.info(f"Patch order_db in db.")
        order_db = await self.orders_repository.patch(order_id, modify_orders_input)
        self.api_response.logger.info(f"order_db: {order_db}")
        return order_db

    async def delete_order_by_id(self, order_id: str) -> None:
        self.api_response.logger.info(f"Init delete order from db, order_id: {order_id}")
        await self.orders_repository.soft_delete(order_id)
