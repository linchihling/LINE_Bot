import logging
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
from linebot_logic.linebot_handler import handle_text_message, handle_follow

# Logger setup
logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)

# RotatingFileHandler
fh = RotatingFileHandler("logs/bot.log", maxBytes=2000000, backupCount=5)
fh.setLevel(logging.INFO)

# StreamHandler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s - %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

# LINE bot Webhook URL
LINE_CHANNEL_ACCESS_TOKEN = "dkDBAvyW1juKypag2NUUzo2eS/2uTqbEZfGf+nkSFxFscnel4Av/hHotyXa1i+4qNwf1/Td4ZpkLQYhJOrZL3z+vWNdYkJ9vJUEc0o9/PUZMwrZnjRUZE9p6BGATAQ3ZlKifeWDMWpFH4UXh1zjwuAdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "1d62be08d3e7008aa2c6e5fcab9eede1"

# Initialize the LINE API Client
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

router = APIRouter(
    prefix="/webhooks/bot",
    tags=["bot"],
    responses={404: {"description": "Not found"}},
)

@router.post("/line")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="chatbot handle body error.")
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    handle_text_message(event, messaging_api)

@handler.add(FollowEvent)
def handle_follow_event(event):
    handle_follow(event, messaging_api)
