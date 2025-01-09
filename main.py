from fastapi import FastAPI
from routers import bot_push, ty_scrap

app = FastAPI()

app.include_router(ty_scrap.router)
app.include_router(bot_push.router)

