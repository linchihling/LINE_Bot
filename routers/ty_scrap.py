from fastapi import APIRouter, Request, Header
from fastapi.responses import JSONResponse
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

from linebot_logic.ty_scrap_handler import handle_text_message
from logger import setup_logger 

logger = setup_logger("ty_scrap", "logs/ty_scrap.log")

# Initialize the LINE API Client
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN_TY_SCRAP'))
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET_TY_SCRAP'))
WEBHOOKS_URL = os.getenv('WEBHOOKS_URL_TY_SCRAP')
group_id = os.getenv('GROUP_ID_TY_SCRAP')

# Limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=WEBHOOKS_URL,
    tags=["ty_scrap"],
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


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    handle_message, handle_result = handle_text_message(event, messaging_api)
    logger.info(f"handle message : {handle_message}")
    if handle_result:
        logger.info(handle_result)


