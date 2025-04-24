from pydantic import BaseModel, EmailStr, SecretStr
from typing import Optional, List

class UsersInput(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    rol: str
    restaurantes: str


#esto es una prueba para el pacth
class UsersUpdateInput(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    rol: Optional[str] = None
    restaurantes: Optional[str] = None


class LoginData(BaseModel):
    username: str
    password: str