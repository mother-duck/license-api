from os import environ
from supabase import acreate_client

async def async_client():
    supabase_client = await acreate_client(
        supabase_url=environ.get("SUPABASE_URL"),
        supabase_key=environ.get("SUPABASE_KEY")
    )

    return supabase_client
