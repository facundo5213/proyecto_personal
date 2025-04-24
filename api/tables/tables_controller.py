from fastapi import APIRouter, Request, Response, status, Depends, HTTPException
from core.db import get_mongo_db

from api.tables.tables_service import TablesService as Service
from api.employees.employees_service import EmployeesService
from models.tables import TablesModel  as Model
from schemas.tables import TablesInput as Input, TablesUpdateInput as InputPach, AssignInput

from utils.exceptions.response_handler import response_handler
from schemas.response import ResponseBase
from utils.presentation.response import ApiResponse
from utils.oauth.auth import get_user_current



ITEM = "table"

###################################################################################################

tables_router: APIRouter = APIRouter(prefix="/v1/tables")

@tables_router.post(
    "",
    tags=["Tables"],
    description=f"Create {ITEM}"
)
@response_handler(response_status=status.HTTP_200_OK)
async def create(
        request: Request,
        response: Response,
        _input: Input,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
        token: str = Depends(get_user_current),
) -> ResponseBase[Model]:
    api_response.logger.info(f"Init create {ITEM}")
    service = Service(api_response, main_db) ##
    item_db = await service.add(_input) ##
    api_response.logger.info(f"Finish create {ITEM}: {item_db}") ##
    return item_db

@tables_router.get(
    "",
    tags=["Tables"],
    description=f"Get {ITEM}s"
)
@response_handler(response_status=status.HTTP_200_OK)
async def get(
    request:Request,
    response:Response,
    api_response=Depends(ApiResponse),
    main_db=Depends(get_mongo_db),
    token: str = Depends(get_user_current),
) -> ResponseBase[list[Model]]:
    api_response.logger.info(f"Init get all {ITEM}")
    service = Service(api_response, main_db)
    items_db = await service.get()
    api_response.logger.info(f"Finish get {ITEM}: {items_db}")
    return items_db

###hasta aca
@tables_router.get(
    "/{table_id}",
    tags=["Tables"],
    description=f"Get {ITEM} by id"
)
@response_handler(response_status=status.HTTP_200_OK)
async def get_by_id(
        request: Request,
        response: Response,
        table_id: str,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
        token: str = Depends(get_user_current),
) -> ResponseBase[Model]:
    api_response.logger.info(f"Init get {ITEM}")
    service = Service(api_response, main_db)
    item_db = await service.get_by_id(table_id)
    api_response.logger.info(f"Finish get {ITEM}: {item_db}")
    return item_db

@tables_router.patch(
    "/{table_id}",
    tags=["Tables"],
    description=f"Modify {ITEM} by id"
)
@response_handler(response_status=status.HTTP_200_OK)
async def modify_by_id(
        request: Request,
        response: Response,
        table_id: str,
        modify_input: InputPach,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
        token: str = Depends(get_user_current),
) -> ResponseBase[Model]:
    api_response.logger.info(f"Init modify {ITEM}")
    service = Service(api_response, main_db)
    item_db = await service.change(table_id, modify_input)
    api_response.logger.info(f"Finish modify {ITEM}: {item_db}")
    return item_db



@tables_router.delete(
    "/{table_id}",
    tags=["Tables"],
    description=f"Delete {ITEM} by id"
)
@response_handler(response_status=status.HTTP_200_OK)
async def delete_by_id(
        request: Request,
        response: Response,
        table_id: str,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
        token: str = Depends(get_user_current),
) -> ResponseBase:
    api_response.logger.info(f"Init delete {ITEM}")
    service = Service(api_response, main_db)
    item_db = await service.delete_by_id(table_id)
    api_response.logger.info(f"Finish delete {ITEM}: {item_db}")
    return 



@tables_router.patch(
    "/{table_id}/assign",
    tags=["Tables"],
    description=f"Assign table to employee"
)
@response_handler(response_status=status.HTTP_200_OK)
async def assign_table(
        request: Request,
        response: Response,
        table_id: str,
        assign_input: AssignInput,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
        token: str = Depends(get_user_current),
) -> ResponseBase[Model]:
    api_response.logger.info(f"Init assign table {table_id} to employee {assign_input.identifier}")
    service = Service(api_response, main_db)
    service_employee = EmployeesService(api_response, main_db)

    # Obtener el empleado por su identificador
    employee = await service_employee.get_employee_by_identifier(assign_input.identifier)
    if employee is None:
        api_response.logger.error(f"Employee with identifier {assign_input.identifier} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
    # Asignar la mesa al empleado
    try:
        item_db = await service.assign_table(table_id, assign_input.identifier)
        print(item_db)
        api_response.logger.info(f"Finish assign table {table_id} to employee {employee}: {item_db}")
        return item_db
    except Exception as e:
        api_response.logger.error(f"Error assigning table {table_id} to employee {employee}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    



@tables_router.patch(
    "/{table_id}/unassign",
    tags=["Tables"],
    description=f"Unassign table to employee"
)
@response_handler(response_status=status.HTTP_200_OK)
async def unassign_table(
        request: Request,
        response: Response,
        table_id: str,
        assign_input: AssignInput,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
        token: str = Depends(get_user_current),
) -> ResponseBase[Model]:
    api_response.logger.info(f"Init Unassign table {table_id} to employee {assign_input.identifier}")
    service = Service(api_response, main_db)
    service_employee = EmployeesService(api_response, main_db)

    # Obtener el empleado por su identificador
    employee = await service_employee.get_employee_by_identifier(assign_input.identifier)
    if employee is None:
        api_response.logger.error(f"Employee with identifier {assign_input.identifier} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
    # Asignar la mesa al empleado
    try:
        item_db = await service.unassign_table(table_id, assign_input.identifier)
        print(item_db)
        api_response.logger.info(f"Finish unassign table {table_id} to employee {employee}: {item_db}")
        return item_db
    except Exception as e:
        api_response.logger.error(f"Error unassigning table {table_id} to employee {employee}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    


@tables_router.patch(
    "/{table_id}/close",
    tags=["Tables"],
    description=f"Close table"
)
@response_handler(response_status=status.HTTP_200_OK)
async def close_table(
        request: Request,
        response: Response,
        table_id: str,
        #assign_input: AssignInput,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
        token: str = Depends(get_user_current),
) -> ResponseBase[Model]:
    api_response.logger.info(f"Init change status of table {table_id} to 'close'")
    service = Service(api_response, main_db)
    item_db = await service.change_status(table_id, "close")
    api_response.logger.info(f"Finished modifying table status to 'close': {item_db}")
    return item_db

@tables_router.patch(
    "/{table_id}/available",
    tags=["Tables"],
    description=f"available table"
)
@response_handler(response_status=status.HTTP_200_OK)
async def available_table(
        request: Request,
        response: Response,
        table_id: str,
        #assign_input: AssignInput,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
        token: str = Depends(get_user_current),
) -> ResponseBase[Model]:
    api_response.logger.info(f"Init change status of table {table_id} to 'available'")
    service = Service(api_response, main_db)
    item_db = await service.change_status(table_id, "available")
    api_response.logger.info(f"Finished modifying table status to 'available': {item_db}")
    return item_db