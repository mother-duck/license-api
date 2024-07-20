import datetime
from base64 import b64decode
from os import environ
from jose import jwt
from typing import Annotated
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from api import utils
from api.repositories import UserRepository
from api.entities import models

def env(key: str) -> str:
    value = environ.get(key)
    if value is None:
        raise ValueError(f"Environment variable {key} is not set")
    return value

bearer = HTTPBearer()

def authorization_credentails(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(bearer)]
):
    token = credentials.credentials
    return token

async def verify_user(
        token: Annotated[str, Depends(authorization_credentails)],
        user_repository: Annotated[UserRepository, Depends(UserRepository)]
    ) -> models.User:
    payload = utils.decode_jwt(token)
    access_token = models.AccessToken.model_validate(payload)
    user = await user_repository.get_user(access_token.sub)
    return user

def utcnow() -> datetime.datetime:
    now = datetime.datetime.now(datetime.UTC)
    return now

def date_after(days: int) -> datetime.datetime:
    now = utcnow()
    after = now + datetime.timedelta(days=days)
    return after

def encode_jwt(payload: dict, algorithm: str = 'HS256') -> str:
    private_key = env('PRIVATE_KEY')
    token = jwt.encode(payload, key=private_key, algorithm=algorithm) 
    return token

def decode_jwt(token: str, algorithm: str = 'HS256') -> dict:
    private_key = env('PRIVATE_KEY')
    payload = jwt.decode(token, key=private_key, algorithms=algorithm)
    return payload
