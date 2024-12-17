from fastapi import FastAPI
from routers import bot, bot_test, rebar

app = FastAPI()

app.include_router(bot.router)
app.include_router(rebar.router)
app.include_router(bot_test.router)

