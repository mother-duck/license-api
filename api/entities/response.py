from typing import Union
from datetime import datetime
from pydantic import BaseModel

class AuthResponse(BaseModel):
    access_token: str

class UserResponse(BaseModel):
    name: str

class UserLicenseResponse(BaseModel):
    service: str
    expires_at: Union[datetime, None]
