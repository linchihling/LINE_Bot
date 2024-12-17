from pydantic import BaseModel
from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    ImageMessage,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

from linebot_logic.bot_handler import handle_text_message
from logger import setup_logger 

logger = setup_logger("ty_bot", "logs/ty_bot.log")

# Initialize the LINE API Client
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
WEBHOOKS_URL = os.getenv('WEBHOOKS_URL_BOT')
group_id = os.getenv('GROUP_ID')

# Limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=WEBHOOKS_URL,
    tags=["bot"],
    responses={404: {"description": "Not found"}}
)

def limit_error():
    logger.warning("Rate limit triggered during LINE webhook")
    return 1


@router.post("/line")
@limiter.limit("2/minute",error_message=limit_error)
async def callback(request: Request, x_line_signature: str = Header(None)):
    client_ip = get_remote_address(request)
    logger.info(f"Incoming request from IP: {client_ip} - Path: {request.url.path}")
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        logger.warning(f"Invalid signature from IP: {client_ip}")
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})
    return {"message": "OK"}


class NotifyRequest(BaseModel):
    rolling_line: str
    message: str
    image_path: str


@router.post("/notify")
@limiter.limit("10/hour")
async def push_message(request: Request, request_body: NotifyRequest):
    try:
        # request data
        rolling_line = request_body.rolling_line
        text_message = request_body.message
        img_path = request_body.image_path
        
        # push
        image_path = f"https://linebot.tunghosteel.com:5003/rl{rolling_line}/{img_path}"
        push_message_request = PushMessageRequest(
            to=group_id,
            messages=[
                TextMessage(text=text_message),
                ImageMessage(original_content_url=image_path, preview_image_url=image_path),
            ]
        )
        messaging_api.push_message(push_message_request)

    except Exception as e:
        print(f"Error pushing message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send push message.")
    
    return {"message": "Push message sent successfully."}

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    handle_message, handle_result = handle_text_message(event, messaging_api)
    logger.info(f"handle message : {handle_message}")
    if handle_result:
        logger.info(handle_result)


