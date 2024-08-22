from logging.handlers import RotatingFileHandler
from fastapi import APIRouter, Request, Header, HTTPException
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent
from linebot_logic.bot_handler import handle_text_message, handle_follow
import os

# Initialize the LINE API Client
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
webhooks_url = os.getenv('WEBHOOKS_URL_BOT')

router = APIRouter(
    prefix=webhooks_url,
    tags=["bot"],
    responses={404: {"description": "Not found"}},
)

@router.post("/line")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        # raise HTTPException(status_code=400, detail="chatbot handle body error.")
        pass
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    handle_text_message(event, messaging_api)

@handler.add(FollowEvent)
def handle_follow_event(event):
    handle_follow(event, messaging_api)
