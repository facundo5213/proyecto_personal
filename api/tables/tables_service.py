from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from utils.presentation.response import ApiResponse
from fastapi import HTTPException, status
from pymongo import ReturnDocument
from utils.presentation.errors import AlreadyExistsException, NotFoundException
from models.employee import EmployeeModel
from models.tables import TablesModel as Modelo_ 
from repositories.tables import TableRepository as Repository_
from schemas.tables import TablesInput as Schemas_ , TablesUpdateInput
from typing import List

ITEM = "tables"

class TablesService:
    def __init__(self, api_response: ApiResponse, main_db: AsyncIOMotorDatabase):
        self.api_response = api_response
        self.main_db = main_db
        self.repository = Repository_(self.main_db)

        self.employee_collection: AsyncIOMotorCollection = self.main_db.get_collection('employee')
        self.tables_collection: AsyncIOMotorCollection = self.main_db.get_collection('tables')

    async def validate_table(self, input: Schemas_, table_id: str = None):
        """Método de validación reutilizable para 'room_id' y 'table_number'."""
        
        # Si el room_id es proporcionado, validamos que la sala exista
        if input.room_id:
            existing_rooms = await self.main_db.rooms.find_one({"_id": input.room_id})
            if not existing_rooms:
                raise NotFoundException(f"Room with id {input.room_id} not found")
        
        # Si no se pasa el room_id en el PATCH, obtenemos el room_id desde el table_id
        if not input.room_id and table_id:
            # Buscar la mesa actual para obtener el room_id
            existing_table = await self.main_db.tables.find_one({"_id": table_id})
            if not existing_table:
                raise NotFoundException(f"Table with id {table_id} not found")
            input.room_id = existing_table["room_id"]  # Asignar el room_id de la mesa existente
        
        # Si table_number está presente, validamos si ya existe en la misma sala
        if input.table_number:
            filter_query = {"table_number": input.table_number, "room_id": input.room_id}
            if table_id:
                filter_query["_id"] = {"$ne": table_id}  # Excluir la mesa actual en las validaciones de update

            # Verificar si existe otra mesa con el mismo número en la misma sala
            existing_tables = await self.main_db.tables.find_one(filter_query)
            if existing_tables:
                raise AlreadyExistsException(f"Table number {input.table_number} already registered in room {input.room_id}")

    #metodo para agregar item
    async def add(self, input: Schemas_) -> Modelo_:
        self.api_response.logger.info(f"Create {ITEM} in db.")
        await self.validate_table(input)
        item_db = await self.repository.create(input)
        self.api_response.logger.info(f"{ITEM}_db: {item_db}")
        return item_db
    
    #metodo para traer todos los restaurant - aun falta el filtro de usuario o restaurant
    async def get(self) -> list[Modelo_]:
        self.api_response.logger.info("Init get {ITEM} from db.")
        item_db = await self.repository.get_all_actives()
        self.api_response.logger.info(f"employes: {item_db}")
        return item_db
    
    #metodo para traer un empleado en particular
    async def get_by_id(self, _id: str) -> Modelo_:
        self.api_response.logger.info(f"Init get {ITEM} from db, employe_id: {_id}")
        item_db = await self.repository.get_active_by_id(_id)
        self.api_response.logger.info(f"{ITEM}_db: {_id}")
        return item_db
    
    #metodo para cambiar un empleado
    async def change(self, _id: str, modify_input: TablesUpdateInput) -> Modelo_:
        self.api_response.logger.info(f"Get {ITEM} from db, {ITEM}_id: {_id}")

        item_db = await self.repository.get_active_by_id(_id)
        if not item_db:
            self.api_response.logger.warning(f"{ITEM} with id {_id} not found.")
            raise NotFoundException(f"{ITEM} with id {_id} not found.")
        
        self.api_response.logger.info(f"{ITEM}_db: {item_db}")

        await self.validate_table(modify_input, _id)

        self.api_response.logger.info(f"Patch {ITEM}_db in db.")
        
        item_db = await self.repository.patch(_id, modify_input)
        self.api_response.logger.info(f"{ITEM}_db: {item_db}")
        return item_db
    
    async def change_status(self, _id: str, status: str) -> Modelo_:
        self.api_response.logger.info(f"Get {ITEM} from db, {ITEM}_id: {_id}")
        item_db = await self.repository.get_active_by_id(_id)
        if not item_db:
            self.api_response.logger.warning(f"{ITEM} with id {_id} not found.")
            return None
        
        self.api_response.logger.info(f"Updating status of {ITEM}_db in db.")
        updated_item_db = await self.tables_collection.find_one_and_update(
        {"_id": _id},
        {"$set": {"status": status}},
        return_document=ReturnDocument.AFTER
        )
        item_db = await self.repository.get_active_by_id(_id)
        self.api_response.logger.info(f"Updated {ITEM}_db: {status}")
        return updated_item_db
    #metodo para pasar delete en true
    async def delete_by_id(self,_id:str) -> Modelo_:
        self.api_response.logger.info(f"Init delete {ITEM} from db, {ITEM}_id: {_id}")
        instance = await self.repository.soft_delete(_id)
        return instance


    async def assign_table(self, table_id: str, employee_identifier: int) -> dict:
        # Obtener el empleado
        employee = await self.employee_collection.find_one({"identifier": employee_identifier})
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        
        # Obtener la mesa
        table = await self.tables_collection.find_one({"_id": table_id})
        if not table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
        
        assigned_tables = employee.get('assigned_tables', [])
        #Verifico si ya existe esta messa asignada en el empleado
        if any(table.get('table_id') == table_id for table in assigned_tables):
            print("Mesa existente")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Table is already assigned to this employee")
        
        table_assigned = {"table_id": table_id, "table_number": table.get('table_number')}
        assigned_tables.append(table_assigned)
        # Actualizar el empleado en la base de datos
        await self.employee_collection.update_one(
            {"identifier": employee_identifier},
            {"$set": {"assigned_tables": assigned_tables}}
        )
        # Asignar el empleado a la mesa
        await self.tables_collection.update_one(
            {"_id": table_id},
            {"$set": {"assigned_employee": employee["_id"]}}
        )
        table_db = await self.tables_collection.find_one({"_id": table_id})
        self.api_response.logger.info(f"Table {table_id} assigned to employee {employee_identifier}.")
        return table_db

    async def unassign_table(self, table_id: str, employee_identifier: int) -> dict:
        # Obtener el empleado
        employee = await self.employee_collection.find_one({"identifier": employee_identifier})
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        # Obtener la mesa
        table = await self.tables_collection.find_one({"_id": table_id})
        if not table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
        
        assigned_tables = employee.get('assigned_tables', [])
        #Verifico si ya existe esta messa asignada en el empleado
        if not any(table.get('table_id') == table_id for table in assigned_tables):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Table is not assigned to this employee")
        assigned_tables = [t for t in assigned_tables if t.get('table_id') != table_id]
        # Actualizar el empleado en la base de datos
        await self.employee_collection.update_one(
            {"identifier": employee_identifier},
            {"$set": {"assigned_tables": assigned_tables}}
        )
        # Asignar el empleado a la mesa
        await self.tables_collection.update_one(
            {"_id": table_id},
            {"$set": {"assigned_employee": ""}}
        )
        table_db = await self.tables_collection.find_one({"_id": table_id})
        self.api_response.logger.info(f"Table {table_id} assigned to employee {employee_identifier}.")
        return table_db
        

    async def get_tables_by_room_id(self, room_id: str) -> List[Modelo_]:
        tables_cursor = self.main_db.tables.find({"room_id": room_id})  # Consultar por room_id
        tables_list = await tables_cursor.to_list(length=None)  # Convertir el cursor a lista
        return tables_list
    
    async def delete_tables_bc_delete_room(self, room_id) -> List[Modelo_]:
        tables_list = await self.get_tables_by_room_id(room_id) # Obtenemos la lista de tables pertenecientes a la room
        tables_list_deleted = []
        for table in tables_list: # Iteramos cada table
            table_deleted = await self.delete_by_id(table["_id"]) # Eliminamos la table una por una
            tables_list_deleted.append(table_deleted.model_dump()) # Almacenamos cada table en una lista
        return tables_list_deleted
