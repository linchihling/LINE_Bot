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
from linebot.v3.webhooks import MessageEvent, ImageMessageContent, FollowEvent
import traceback

router = APIRouter()

# Logger setup
logger = logging.getLogger("rebar_bot_logger")
logger.setLevel(logging.INFO)

# RotatingFileHandler
fh = RotatingFileHandler("logs/rebar_bot.log", maxBytes=2000000, backupCount=5)
fh.setLevel(logging.INFO)

# StreamHandler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

# LINE bot Webhook URL
LINE_CHANNEL_ACCESS_TOKEN = "PNTQ48ZPiiWOv0YBbsbBRJ2ZzdlZD719spRZKFChQEP0M8e7E4oIu0N3tqF8kOL+qbDMoKmk496hYchNI+Q7JnujrsK5K7nwssAcUdMj2qQnzSxuKaY3CSEsHS7xE0sgrPMOtDSCtvfLaLeTC04BNgdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "96a02726d0ec48f68b50696deaaa9184"

# Initialize the LINE API Client
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)

handler = WebhookHandler(LINE_CHANNEL_SECRET)

@router.post("/webhook")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")
    return "OK"

# Import the line bot handlers from linebot_logic
from linebot_logic.rebar_counter_handler import handle_image_message, handle_follow

handler.add(MessageEvent, message=ImageMessageContent)(lambda event: handle_image_message(event, messaging_api))
handler.add(FollowEvent)(lambda event: handle_follow(event, messaging_api))
