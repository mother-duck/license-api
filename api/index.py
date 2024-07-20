from fastapi import FastAPI
from api.routes import user

app = FastAPI(
    title="Vercel FastAPI",
    description="FastAPI hosted on Vercel",
    docs_url="/docs",
    redoc_url=None
)

app.include_router(user.router)
