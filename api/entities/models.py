from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class AccessToken(BaseModel):
    sub: str
    iat: int
    exp: int
    tty: TokenType
    svc: list[str]

class SignIn(BaseModel):
    license_key: str
    auth_key: str

class AuthInfo(BaseModel):
    auth_key: str

class SignUp(BaseModel):
    name: str

class Auth(BaseModel):
    uid: str
    name: str
    hash: str | None
    salt: str | None
    created_at: datetime

class User(BaseModel):
    uid: str
    name: str

class CreateLicense(BaseModel):
    uid: str
    service: str
    expires_in: int

class License(BaseModel):
    uid: str
    service: str
    expires_at: datetime | None

class Refresh(BaseModel):
    token: str
    service: str

class AuthToken(BaseModel):
    access_token: str

class CreateAction(BaseModel):
    data: dict | None = Field(default={})


class UserAction(BaseModel):
    uid: str
    service: str
    action: str
    data: dict | None
