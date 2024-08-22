from fastapi import APIRouter, Request, Header
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent
import os

from linebot_logic.rebar_handler import handle_text_message, handle_follow
from logger import setup_logger
logger = setup_logger("rebar", "logs/rebar.log")

# Initialize the LINE API Client
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN_3'))
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET_3'))
webhooks_url = os.getenv('WEBHOOKS_URL_REBAR')

router = APIRouter(
    prefix=webhooks_url,
    tags=["rebar"],
    responses={404: {"description": "Not found"}},
)

@router.post("/line")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        logger.error("Invalid signature error")
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text(event):
    handle_text_message(event, logger, messaging_api)

@handler.add(FollowEvent)
def handle_follow_event(event):
    handle_follow(logger, event, messaging_api)



