import datetime
from fastapi import Depends
from typing import Annotated
from supabase import AClient as Supabase
from api.saas.supabase import async_client
from api.entities import models

class LicenseRepository:
    supabase: Supabase

    def __init__(self, supabase: Annotated[Supabase, Depends(async_client)]):
        self.supabase = supabase

    async def create_license(self, uid: str, service: str, expires_in: int):
        expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=expires_in)

        result = await self.supabase \
            .table("licenses") \
            .upsert({
                "uid": uid,
                "service": service,
                "expires_at": expires_at.isoformat()
            }) \
            .execute()

        license = result.data[0]

        return models.License(
            uid=license["uid"],
            service=license["service"],
            expires_at=license["expires_at"]
        )

    async def find_licenses(self, uid: str) -> list[models.License]:
        result = await self.supabase \
            .table("licenses") \
            .select("*") \
            .eq("uid", uid) \
            .execute()
        
        return [
            models.License(
                uid=license['uid'],
                service=license['service'],
                expires_at=license['expires_at']
            ) for license in result.data
        ]
