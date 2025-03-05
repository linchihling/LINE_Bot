import os
from pydantic import BaseModel
from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
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
    send_notification
)
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize the LINE API Client
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN_PUSHBOT'))
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET_PUSHBOT'))
WEBHOOKS_URL = os.getenv('WEBHOOKS_URL_PUSHBOT')
group_id_push_ty = os.getenv('GROUP_ID_PUSHBOT_TY_SCRAP')
# group_id_push_project2 = os.getenv('GROUP_ID_PUSHBOT_TEST_PROJECT')
line_notify_token = os.getenv('LINE_NOTIFY_TOKEN')
ntfy_topic = os.getenv('NTFY_TOPIC')

# Limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=WEBHOOKS_URL,
    tags=["bot_push"],
    responses={404: {"description": "Not found"}}
)

def limit_error():
    logger.warning("Rate limit triggered during LINE webhook")
    return 1


@router.post("/line")
@limiter.limit("2/minute",error_message=limit_error)
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


class NotifyRequest(BaseModel):
    rolling_line: str
    message: str
    image_path: str


@router.post("/notify/ty_scrap")
@limiter.limit("10/3minute")
async def push_message(request: Request, request_body: NotifyRequest):
    try:
        rolling_line = request_body.rolling_line
        text_message = request_body.message
        img_path = request_body.image_path
        
        image_url = f"https://linebot.tunghosteel.com:5003/rl{rolling_line}/{img_path}"

        
        # Push message to Line Group
        send_notification(send_to_line_group, messaging_api, group_id_push_ty, text_message, image_url)

        # NTFY Notification
        send_notification(send_ntfy_notification, ntfy_topic, text_message, image_url)

        # LINE Notify
        send_notification(send_line_notify, line_notify_token, text_message, image_url)
        
        return {"status": "success", "message": "Notification sent successfully"}

    except Exception as e:
        logger.error(f"Error in push_message: {str(e)}", exc_info=True)  
        raise HTTPException(status_code=500, detail="Internal Server Error")
