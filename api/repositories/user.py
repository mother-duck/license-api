from fastapi import Depends
from typing import Annotated
from supabase import AClient as Supabase
from api import utils
from api.saas.supabase import async_client
from api.entities import errors, models

class UserRepository:
    supabase: Supabase

    def __init__(self, supabase: Annotated[Supabase, Depends(async_client)]):
        self.supabase = supabase

    async def get_user(self, uid: str) -> models.User:
        result = await self.supabase \
            .table("auth") \
            .select("*") \
            .eq("uid", uid) \
            .maybe_single() \
            .execute()

        if not result.data:
            raise errors.NotFoundException()

        user = models.User(
            uid=result.data['uid'],
            name=result.data['name'],
            created_at=result.data['created_at']
        )

        return user

    async def sign_in(self, data: models.SignIn) -> models.Auth:
        result = await self.supabase \
            .table('auth') \
            .select("*") \
            .eq("uid", data.license_key) \
            .maybe_single().execute()

        if not result.data:
            raise errors.UnauthorizedException()

        auth = models.Auth(
            uid=result.data['uid'],
            name=result.data['name'],
            hash=result.data['hash'],
            salt=result.data['salt'],
            created_at=result.data['created_at']
        )

        return auth

    async def get_auth_by_key(self, key: str) -> models.Auth:
        result = await self.supabase \
            .table('auth') \
            .select("*") \
            .eq("hash", key) \
            .maybe_single().execute()

        if not result.data:
            raise errors.NotFoundException()

        auth = models.Auth(
            uid=result.data['uid'],
            name=result.data['name'],
            hash=result.data['hash'],
            salt=result.data['salt'],
            created_at=result.data['created_at']
        )

        return auth

    async def sign_up(self, data: models.SignUp) -> models.Auth:
        params = { "name": data.name }
        results = await self.supabase \
            .table("auth") \
            .insert([params]) \
            .execute()

        auth = models.Auth.model_validate(results.data[0])
        return auth

    async def update_hash(self, data: models.SignIn):
        await self.supabase \
            .table('auth') \
            .update({
                'hash': data.auth_key
            }) \
            .eq('uid', data.license_key).execute()

    async def create_user_action(self, uid: str, service: str, action: str, data: dict) -> models.UserAction:
        result = await self.supabase \
            .table('actions') \
            .insert({
                'uid': uid,
                'service': service,
                'action': action,
                'data': data
            }) \
            .execute()

        action = result.data[0]
        return models.UserAction(
            uid=action['uid'],
            service=action['service'],
            action=action['action'],
            data=action['data'] if 'data' in action else None,
        )
    
    async def get_user_actions(self, uid: str, service: str, action: str) -> list[models.UserAction]:
        before = utils.start_of_today()
        result = await self.supabase \
            .table('actions') \
            .select('*') \
            .eq('uid', uid) \
            .eq('service', service) \
            .eq('action', action) \
            .filter('created_at', 'gte', before) \
            .execute()

        return [
            models.UserAction(
                uid=action['uid'],
                service=action['service'],
                action=action['action'],
                data=action['data'] if 'data' in action else None,
            )
            for action in result.data
        ]
