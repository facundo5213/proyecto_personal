from motor.motor_asyncio import AsyncIOMotorDatabase



from models.users import UsersModel , UserResponseModel
from repositories.users import UsersRepository, UsersRepositoryResponse, UsersRepositoryLogin
from schemas.users import UsersInput , UsersUpdateInput
from utils.presentation.response import ApiResponse
from werkzeug.security import generate_password_hash, check_password_hash
from utils.presentation.errors import AlreadyExistsException
from fastapi.exceptions import HTTPException


class UsersService:
    def __init__(self, api_response: ApiResponse, main_db: AsyncIOMotorDatabase):
        self.api_response = api_response
        self.main_db = main_db
        self.users_repository = UsersRepository(self.main_db)
        self.users_repository_response = UsersRepositoryResponse(self.main_db)
        self.user_repository_login = UsersRepositoryLogin(self.main_db)


    #MODIFICADO PARA MANEJO DE HASH PASSWORD
    async def add_user(self, users_input: UsersInput) -> UsersModel:
        self.api_response.logger.info(f"Create user_db in db.")
        
        # Generar hash de la contraseña
        hashed_password = generate_password_hash(users_input.password, "pbkdf2:sha256:30", 30)
        
        user_data = users_input.model_dump()
        user_data['password'] = hashed_password
        
        # Crear un nuevo objeto UsersModel con los datos actualizados
        updated_users_input = UsersModel(**user_data)

        # Validar la existencia de ese usuario
        existing_user = await self.main_db.users.find_one({"email": users_input.email})
        if existing_user:
            raise AlreadyExistsException("Email already registered")
        
        # Crear el usuario en la base de datos
        user_db = await self.users_repository.create(updated_users_input)

        # Elimino el campo de password para no devolverlo
        user_db_dict = user_db.model_dump() # Convierte el objeto a dict
        user_db_dict['password'] = '********'  # Ocultar la contraseña

        self.api_response.logger.info(f"user_db: {user_db_dict}")

        # Devolver el objeto con el ID correcto
        return user_db_dict



    async def get_users(self) -> list[UserResponseModel]:
        self.api_response.logger.info("Init get users from db.")
        users_db = await self.users_repository_response.get_all_actives() #solucionado haciendo otro user_repository
        self.api_response.logger.info(f"users_db: {users_db}")
        return users_db

    async def get_user_by_id(self, user_id: str) -> UserResponseModel:
        self.api_response.logger.info(f"Init get user from db, user_id: {user_id}")
        user_db = await self.users_repository_response.get_active_by_id(user_id)
        self.api_response.logger.info(f"user_db: {user_db}")
        return user_db
    

    async def get_user_by_email(self, user_mail: str, password: str) -> UserResponseModel:
        self.api_response.logger.info(f"Init get user from db, user mail: {user_mail}")
        user_db = await self.user_repository_login.get_by_email(user_mail)
        if not user_db:
            self.api_response.logger.info(f"User not found: {user_mail}")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        # Verifica la contraseña
        if not check_password_hash(user_db['password'], password):
            self.api_response.logger.info(f"Password mismatch for user: {user_mail}")
            #raise HTTPException(status_code=400, detail="Invalid credentials")
            return None
 
        self.api_response.logger.info(f"user_db: {user_db}")
        return user_db
    

    async def change_user(self, user_id: str, modify_users_input: UsersInput) -> UsersModel:
        self.api_response.logger.info(f"Get user from db, user_id: {user_id}")
        user_db = await self.users_repository.get_active_by_id(user_id)
        self.api_response.logger.info(f"user_db: {user_db}")
        self.api_response.logger.info(f"Patch user_db in db.")
        user_db = await self.users_repository.patch(user_id, modify_users_input)
        self.api_response.logger.info(f"user_db: {user_db}")
        return user_db
    

    ############################ESTo ESTOY AGREGANDO###################
    async def change_user_partial(self, user_id: str, modify_users_input: UsersUpdateInput) -> UserResponseModel:
        self.api_response.logger.info(f"Get user from db, user_id: {user_id}")
        user_db = await self.users_repository.get_active_by_id(user_id)
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        self.api_response.logger.info(f"user_db: {user_db}")
        self.api_response.logger.info(f"Patch user_db in db with updates: {modify_users_input}")
        user_db = await self.users_repository.patch(user_id, modify_users_input)
        self.api_response.logger.info(f"user_db: {user_db}")
        user_db.model_dump()
        user_db.password = '********'
        return user_db
    ########################################################################

    async def delete_user_by_id(self, user_id: str) -> None:
        self.api_response.logger.info(f"Init delete user from db, user_id: {user_id}")
        await self.users_repository.soft_delete(user_id)
