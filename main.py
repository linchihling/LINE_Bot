# from fastapi import FastAPI
# from routers import webhooks, bot_test
# app = FastAPI()

# app.include_router(webhooks.router)
# app.include_router(bot_test.router)

# @app.get("/")
# async def root():
#     return {"message": "Hello Kitty!"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=6000)



from fastapi import FastAPI, APIRouter, Header, Request
from linebot import LineBotApi, WebhookHandler

app = FastAPI()
router = APIRouter( prefix="/webhooks",
    tags=["chatbot"],
    responses={404: {"description": "Not found"}},)

@router.post("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

app.include_router(router)

@app.get("/")
async def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6000)