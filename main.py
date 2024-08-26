from fastapi import FastAPI
from routers import bot, bot_test

app = FastAPI()

app.include_router(bot.router)
app.include_router(bot_test.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=6000)
