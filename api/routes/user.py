from typing import Annotated
from fastapi import APIRouter, Depends
from api import utils
from api.entities import models, errors, response
from api.repositories import UserRepository, LicenseRepository
from api.utils import verify_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get(
    path="",
    summary="Get user profile",
    description="Get user profile",
)
async def get_user(
    user: Annotated[models.User, Depends(verify_user)],
) -> response.UserResponse:
    return response.UserResponse.model_validate(user.model_dump())

@router.post(
    path="/signup",
    summary="Sign up",
    description="Sign up",
)
async def sign_up(
    data: models.SignUp,
    user_repository: Annotated[UserRepository, Depends(UserRepository)],
) -> models.User:
    auth: models.Auth = await user_repository.sign_up(data)
    user = models.User(
        uid=auth.uid,
        name=auth.name
    )

    return user.model_dump()

@router.post(
    path="/signin",
    summary="Sign in",
    description="User authorization",
)
async def sign_in(
    data: models.SignIn,
    user_repository: Annotated[UserRepository, Depends(UserRepository)],
    license_repository: Annotated[LicenseRepository, Depends(LicenseRepository)],
) -> models.AuthToken:
    auth: models.Auth = await user_repository.sign_in(data)

    if auth.hash is None:
        await user_repository.update_hash(data)
    elif auth.hash != data.auth_key:
        raise errors.UnauthorizedException()

    licenses = await license_repository.find_licenses(uid=auth.uid)

    now = utils.utcnow()
    exp = utils.date_after(1)

    payload = models.AccessToken(
        sub=auth.uid,
        iat=int(now.timestamp() * 1000),
        exp=int(exp.timestamp() * 1000),
        tty=models.TokenType.ACCESS,
        svc=[license.service for license in licenses]
    )

    access_token = utils.encode_jwt(payload.model_dump())

    token = models.AuthToken(
        access_token=access_token
    )

    return token.model_dump()

@router.get(
    path="/service/{service}/action/{action}",
    summary="User actions",
    description="User actions",
)
async def get_user_action(
    service: str,
    action: str,
    user: Annotated[models.User, Depends(verify_user)],
    user_repository: Annotated[UserRepository, Depends(UserRepository)],
):
    actions = await user_repository.get_user_actions(user.uid, service, action)

    return {
        "count": len(actions),
        "data": [action.model_dump() for action in actions]
    }

@router.post(
    path="/service/{service}/action/{action}",
    summary="User action",
    description="User action",
)
async def create_user_action(
    service: str,
    action: str,
    data: models.CreateAction,
    user: Annotated[models.User, Depends(verify_user)],
    user_repository: Annotated[UserRepository, Depends(UserRepository)],
) -> models.UserAction:
    action = await user_repository.create_user_action(user.uid, service, action, data.data)

    return action.model_dump()

@router.post(
    path="/license",
    summary="grant license",
    description="grant user license",
)
async def grant_license(
    data: models.CreateLicense,
    user_repository: Annotated[UserRepository, Depends(UserRepository)],
    license_repository: Annotated[LicenseRepository, Depends(LicenseRepository)],
) -> models.License:
    user: models.User = await user_repository.get_user(uid=data.uid)
    license = await license_repository.create_license(user.uid, data.service, data.expires_in)

    return license.model_dump()
