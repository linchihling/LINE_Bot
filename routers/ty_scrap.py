import os
from fastapi import APIRouter, Request, Header
from fastapi.responses import JSONResponse
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from slowapi import Limiter
from slowapi.util import get_remote_address

from handlers.ty_scrap_handler import TyScrapBotHandler
from utils.factory import setup_logger

logger = setup_logger(__name__)

configuration = Configuration(
    access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN_TY_SCRAP")
)
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)

handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET_TY_SCRAP"))
WEBHOOKS_URL = os.getenv("WEBHOOKS_URL_TY_SCRAP")
group_id = os.getenv("GROUP_ID_TY_SCRAP")
project_name = "ty_scrap"

bot_handler = TyScrapBotHandler(messaging_api)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=WEBHOOKS_URL,
    tags=[project_name],
    responses={404: {"description": "Not found"}},
)


def limit_error():
    logger.warning(
        "Rate limit triggered during LINE webhook", extra={"project": project_name}
    )
    return 1


@router.post("/line")
@limiter.limit("10/minute", error_message=limit_error)
async def callback(request: Request, x_line_signature: str = Header(None)):
    client_ip = get_remote_address(request)
    logger.info(
        f"Incoming request from IP: {client_ip} - Path: {request.url.path}",
        extra={"project": project_name},
    )
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
        return {"message": "OK"}
    except InvalidSignatureError:
        logger.error(
            f"Invalid signature from IP: {client_ip} - Body: {body.decode('utf-8')}",
            extra={"project": project_name},
        )
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    handle_message, handle_result = bot_handler.handle_text_message(event)
    logger.info(f"Handle message: {handle_message}", extra={"project": project_name})
    if handle_result:
        logger.info(handle_result, extra={"project": project_name})
