from motor.motor_asyncio import AsyncIOMotorDatabase
from utils.presentation.response import ApiResponse
from utils.presentation.errors import AlreadyExistsException, NotFoundException
from models.rooms import RoomsModel as modelo_, RoomsModelResponseId
from repositories.rooms import RoomsRepository as Repository_
from schemas.rooms import RoomsInput as Schemas_
from typing import List
from ..tables.tables_service import TablesService

ITEM = "rooms"

class RoomsService:
    def __init__(self, api_response: ApiResponse, main_db: AsyncIOMotorDatabase):
        self.api_response = api_response
        self.main_db = main_db
        self.repository = Repository_(self.main_db)

    #metodo para agregar item
    async def add(self, input: Schemas_) -> modelo_:
        self.api_response.logger.info(f"Create {ITEM} in db.")

        # Valido la existencia del Restaurant asignado
        existing_restaurant = await self.main_db.restaurants.find_one({"_id": input.restaurant_id})
        if not existing_restaurant:
            raise NotFoundException("Invalid restaurant_id")

        # Valido la existencia de esa Room en el Restaurant asignado
        existing_room = await self.main_db.rooms.find_one({"room_number": input.room_number, "restaurant_id": input.restaurant_id})
        if existing_room:
            raise AlreadyExistsException("Room already registered in that restaurant")
        
        # Creamos la Room en el repositorio correspondiente
        item_db = await self.repository.create(input)
        self.api_response.logger.info(f"{ITEM}_db: {item_db}")
        return item_db
    
    #metodo para traer todos los rooms
    async def get(self) -> list[modelo_]:
        self.api_response.logger.info("Init get {ITEM} from db.")
        item_db = await self.repository.get_all_actives()
        self.api_response.logger.info(f"employes: {item_db}")
        return item_db
    
    #metodo para traer un room en particular
    async def get_by_id(self, _id: str) -> RoomsModelResponseId:
        self.api_response.logger.info(f"Init get {ITEM} from db, employe_id: {_id}")
        item_db = await self.repository.get_active_by_id(_id)
        tables_service = TablesService(self.api_response, self.main_db) 
        tables_db = await tables_service.get_tables_by_room_id(_id)
        item_db_dict = item_db.model_dump()  
        item_db_dict["tables"] = tables_db
        self.api_response.logger.info(f"{ITEM}_db: {_id}")
        return item_db_dict


    #metodo para cambiar un room
    async def change(self, _id: str, modify_input: Schemas_) -> modelo_:
        self.api_response.logger.info(f"Get {ITEM} from db, {ITEM}_id: {_id}")
        item_db = await self.repository.get_active_by_id(_id)
        self.api_response.logger.info(f"{ITEM}_db: {item_db}")

        # Valido la existencia del Restaurant asignado
        existing_restaurant = await self.main_db.restaurants.find_one({"_id": modify_input.restaurant_id})
        if not existing_restaurant:
            raise NotFoundException("Invalid restaurant_id")
        
        self.api_response.logger.info(f"Patch {ITEM}_db in db.")
        item_db = await self.repository.patch(_id, modify_input)
        self.api_response.logger.info(f"{ITEM}_db: {item_db}")
        return item_db
    
    #metodo para pasar delete en true
    async def delete_by_id(self,_id:str) -> RoomsModelResponseId:
        self.api_response.logger.info(f"Init delete {ITEM} from db, {ITEM}_id: {_id}")
        # Eliminamos las tables que pertenecen a la room (is_deleted = true)
        tables_service = TablesService(self.api_response, self.main_db) 
        tables_db = await tables_service.delete_tables_bc_delete_room(_id)
        # Eliminamos la room (is_deleted = true)
        instance = await self.repository.soft_delete(_id)
        print(instance)
        item_db_dict = instance.model_dump()  
        item_db_dict["tables"] = tables_db
        return item_db_dict # Devolvemos la room eliminada con una lista de sus tables eliminadas
    
    
    async def get_rooms_by_restaurant_id(self, restaurant_id: str) -> List[modelo_]:
        rooms_cursor = self.main_db.rooms.find({"restaurant_id": restaurant_id, "is_deleted": False})  # Consultar por restaurant_id
        rooms_list = await rooms_cursor.to_list(length=None)  # Convertir el cursor a lista
        return rooms_list
