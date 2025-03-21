import os
import time
from pydantic import BaseModel
from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from linebot.v3 import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent  # noqa F401
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    Configuration,
    ApiClient,
    MessagingApi,
)
from slowapi import Limiter
from slowapi.util import get_remote_address

from utils.notification import (
    send_to_line_group,
    send_ntfy_notification,
    send_line_notify,
    send_notification,
)
from utils.logger import setup_logger

logger = setup_logger(__name__, "line")
logger_ty_scrap = setup_logger(__name__, "ty_scrap")
logger_water_spray = setup_logger(__name__, "water_spray")

# Initialize the LINE API Client
configuration = Configuration(
    access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN_PUSHBOT")
)
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET_PUSHBOT"))
WEBHOOKS_URL = os.getenv("WEBHOOKS_URL_PUSHBOT")
group_id_push_ty = os.getenv("GROUP_ID_PUSHBOT_TY_SCRAP")
group_id_push_water_spray = os.getenv("GROUP_ID_PUSHBOT_TY_WATER_SPRAY")
line_notify_token = os.getenv("LINE_NOTIFY_TOKEN")
ntfy_ty_scrap = os.getenv("NTFY_TY_SCRAP")
ntfy_water_spray = os.getenv("NTFY_WATER_SPRAY")

# Limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=WEBHOOKS_URL,
    tags=["bot_push"],
    responses={404: {"description": "Not found"}},
)


def limit_error():
    logger.warning("Rate limit triggered during LINE webhook")
    return 1


@router.post("/line")
@limiter.limit("5/minute", error_message=limit_error)
async def callback(request: Request, x_line_signature: str = Header(None)):
    client_ip = get_remote_address(request)
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        logger.warning(f"Invalid signature from IP: {client_ip}")
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})
    logger.info(f"Incoming request from IP: {client_ip} - Path: {request.url.path}")
    return {"message": "OK"}


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    message = event.message.text
    token = event.reply_token
    group_id = event.source.group_id
    if message == "!GROUP ID":
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=token,
                messages=[TextMessage(text=f"{group_id}")],
            )
        )


class NotifyRequest_ty_scrap(BaseModel):
    rolling_line: str
    message: str
    image_path: str


class NotifyRequest_water_spray(BaseModel):
    message: str


@router.post("/notify/ty_scrap")
@limiter.limit("10/3minute")
async def push_message(request: Request, request_body: NotifyRequest_ty_scrap):
    logger_ty_scrap.info(f"Received request: {await request.json()}")
    rolling_line = request_body.rolling_line
    text_message = request_body.message
    img_path = request_body.image_path

    image_url = f"https://linebot.tunghosteel.com:5003/rl{rolling_line}/{img_path}"
    try:
        # Push message to Line Group
        send_notification(
            "ty_scrap",
            send_to_line_group,
            messaging_api,
            group_id_push_ty,
            text_message,
            image_url,
        )

        # NTFY Notification
        send_notification(
            "ty_scrap", send_ntfy_notification, ntfy_ty_scrap, text_message, image_url
        )

        # LINE Notify
        send_notification(
            "ty_scrap", send_line_notify, line_notify_token, text_message, image_url
        )

        return {"status": "success", "message": "Notification sent successfully"}

    except Exception as e:
        logger_ty_scrap.error(f"Error in push_message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/notify/water_spray")
@limiter.limit("10/3minute")
async def push_message_water_spray(
    request: Request, request_body: NotifyRequest_water_spray
):

    logger_water_spray.info(f"Received request: {await request.json()}")
    text_message = request_body.message
    date_time = time.time()
    image_url = f"https://linebot.tunghosteel.com:5003/water_spray?{date_time}"
    try:
        # Push message to Line Group
        send_notification(
            "water_spray",
            send_to_line_group,
            messaging_api,
            group_id_push_water_spray,
            text_message,
            image_url,
        )
        # NTFY Notification
        send_notification(
            "water_spray",
            send_ntfy_notification,
            ntfy_water_spray,
            text_message,
            image_url,
        )
        return {"status": "success", "message": "Notification sent successfully"}

    except Exception as e:
        logger_water_spray.error(f"Error in push_message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
