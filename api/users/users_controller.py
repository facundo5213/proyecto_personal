from fastapi import APIRouter, Request, Response, status, Depends

from api.users.users_service import UsersService
from core.db import get_mongo_db
from models.users import UserResponseModel, UsersModel
from schemas.response import ResponseBase
from schemas.users import UsersInput, UsersUpdateInput
from utils.exceptions.response_handler import response_handler
from utils.presentation.response import ApiResponse
from utils.oauth.auth import get_user_current



users_router: APIRouter = APIRouter(prefix="/v1/users")


@users_router.post(
    "",
    tags=["Users"],
    summary="Crear un nuevo usuario",
    description="Endpoint para crear un nuevo usuario en el sistema.",
    response_description="El usuario creado.",
)
@response_handler(response_status=status.HTTP_200_OK)
async def create_users(
        request: Request,
        response: Response,
        users_input: UsersInput,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
) -> ResponseBase[UserResponseModel]:
    api_response.logger.info("Init create user")
    user_service = UsersService(api_response, main_db)
    user = await user_service.add_user(users_input)
    api_response.logger.info(f"Finish create user: {user}")

    return user


@users_router.get(
    "",
    tags=["Users"],
    summary="Obtener todos los usuarios",
    description="Endpoint para obtener todos los usuarios del sistema.",
    response_description="Una lista de usuarios.",
)
@response_handler(response_status=status.HTTP_200_OK)
async def get_users(
        request: Request,
        response: Response,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
        token: str = Depends(get_user_current)
) -> ResponseBase[list[UserResponseModel]]:
    api_response.logger.info("Init get all users")
    user_service = UsersService(api_response, main_db)
    users = await user_service.get_users()
    api_response.logger.info(f"Finish get users: {users}")
    return users


@users_router.get(
    "/{user_id}",
    tags=["Users"],
    summary="Obtener usuario por ID",
    description="Endpoint para obtener un usuario por su ID.",
    response_description="El usuario con el ID especificado.",
)
@response_handler(response_status=status.HTTP_200_OK)
async def get_user(
        request: Request,
        response: Response,
        user_id: str,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
        token: str = Depends(get_user_current)
) -> ResponseBase[UserResponseModel]:
    api_response.logger.info("Init get user")
    user_service = UsersService(api_response, main_db)
    user = await user_service.get_user_by_id(user_id)
    api_response.logger.info(f"Finish get user: {user}")
    return user


@users_router.patch(
    "/{user_id}",
    tags=["Users"],
    summary="Modificar usuario por ID",
    description="Endpoint para modificar un usuario por su ID.",
    response_description="El usuario modificado.",
)
@response_handler(response_status=status.HTTP_200_OK)
async def modify_user(
        request: Request,
        response: Response,
        user_id: str,
        modify_user_input: UsersUpdateInput,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
        token: str = Depends(get_user_current),
) -> ResponseBase[UsersModel]:
    api_response.logger.info("Init modify user")
    user_service = UsersService(api_response, main_db)
    user = await user_service.change_user_partial(user_id, modify_user_input)
    api_response.logger.info(f"Finish modify user: {user}")
    return user



@users_router.delete(
    "/{user_id}",
    tags=["Users"],
    summary="Eliminar usuario por ID",
    description="Endpoint para eliminar un usuario por su ID.",
    response_description="El usuario eliminado.",
)
@response_handler(response_status=status.HTTP_200_OK)
async def delete_user(
        request: Request,
        response: Response,
        user_id: str,
        api_response=Depends(ApiResponse),
        main_db=Depends(get_mongo_db),
        token: str = Depends(get_user_current)
) -> ResponseBase:
    api_response.logger.info("Init delete user")
    user_service = UsersService(api_response, main_db)
    user = await user_service.delete_user_by_id(user_id)
    api_response.logger.info(f"Finish delete user: {user}")
    return