import os
import time
from pydantic import BaseModel
from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from linebot.v3 import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from slowapi import Limiter
from slowapi.util import get_remote_address

from utils.notification import Notifier
from utils.factory import setup_logger

logger = setup_logger(__name__)

# Initialize LINE API Client
configuration = Configuration(
    access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN_PUSHBOT")
)
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET_PUSHBOT"))

# Environment Configurations
WEBHOOKS_URL = os.getenv("WEBHOOKS_URL_PUSHBOT")
group_ids = {
    "ty_scrap": os.getenv("GROUP_ID_PUSHBOT_TY_SCRAP"),
    "water_spray": os.getenv("GROUP_ID_PUSHBOT_TY_WATER_SPRAY"),
    "spark_detection": os.getenv("GROUP_ID_PUSHBOT_TY_SPARK_DETECTION"),
    "dust_detection": os.getenv("GROUP_ID_PUSHBOT_TY_DUST_DETECTION"),
    "pose_detection": os.getenv("GROUP_ID_PUSHBOT_TY_POSE_DETECTION"),
}
ntfy_topics = {
    "ty_scrap": os.getenv("NTFY_TY_SCRAP"),
    "water_spray": os.getenv("NTFY_TY_WATER_SPRAY"),
    "spark_detection": os.getenv("NTFY_TY_SPARK_DETECTION"),
    "dust_detection": os.getenv("NTFY_TY_DUST_DETECTION"),
    "pose_detection": os.getenv("NTFY_TY_POSE_DETECTION"),
}

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=WEBHOOKS_URL,
    tags=["ths_bot"],
    responses={404: {"description": "Not found"}},
)


# Models
class ScrapNotificationRequest(BaseModel):
    rolling_line: str
    message: str
    image_path: str


class ImageNotificationRequest(BaseModel):
    message: str
    image_filename: str


class TextNotificationRequest(BaseModel):
    message: str


# Internal Functions
def _limit_error():
    logger.warning(
        "Rate limit triggered during LINE webhook", extra={"project": "line"}
    )
    return 1


def _send_notification(
    project: str, group_key: str, message: str, image_url: str = None
):
    try:
        notifier = Notifier(project_name=project, messaging_api=messaging_api)
        notifier.send_line(
            group_id=group_ids[group_key], text_message=message, image_url=image_url
        )
        notifier.send_ntfy(
            ntfy_topic=ntfy_topics[project], text_message=message, image_url=image_url
        )
        return {"status": "success", "message": "Notification sent successfully"}
    except Exception as e:
        logger.error(
            f"Error in {project} notification: {str(e)}",
            exc_info=True,
            extra={"project": project},
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@handler.add(MessageEvent, message=TextMessageContent)
def _handle_message(event):
    message = event.message.text
    group_id = event.source.group_id

    if message == "(系統測試，請忽略)":
        logger.info(
            f"Replied with Group ID: {group_id} (from {event.source.user_id})",
            extra={"project": "line"},
        )


# Webhook Endpoint
@router.post("/line")
@limiter.limit("5/minute", error_message=_limit_error)
async def callback(request: Request, x_line_signature: str = Header(None)):
    client_ip = get_remote_address(request)
    body = await request.body()

    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        logger.warning(
            f"Invalid signature from IP: {client_ip}", extra={"project": "line"}
        )
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})

    logger.debug(
        f"Incoming request from IP: {client_ip} - Path: {request.url.path}",
        extra={"project": "line"},
    )
    return {"message": "OK"}


# Notification Routes
@router.post("/notify/ty_scrap")
@limiter.limit("10/3minute")
async def push_ty_scrap(request: Request, body: ScrapNotificationRequest):
    logger.info(
        f"Received request: {await request.json()}", extra={"project": "ty_scrap"}
    )
    image_url = (
        f"https://linebot.tunghosteel.com:5003/rl{body.rolling_line}/{body.image_path}"
    )
    return _send_notification("ty_scrap", "ty_scrap", body.message, image_url)


@router.post("/notify/ty_system_scrap")
@limiter.limit("10/1minute")
async def push_ty_system_scrap(request: Request, body: TextNotificationRequest):
    logger.info(
        f"Received request: {await request.json()}",
        extra={"project": "ty_system_scrap"},
    )
    try:
        notifier = Notifier(project_name="ty_system_scrap", messaging_api=messaging_api)
        notifier.send_line(
            group_id=group_ids["ty_scrap"], text_message=body.message, image_url=None
        )
        return {"status": "success", "message": "Notification sent successfully"}
    except Exception as e:
        logger.error(
            f"Error in sent: {str(e)}",
            exc_info=True,
            extra={"project": "ty_system_scrap"},
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/notify/water_spray")
@limiter.limit("10/3minute")
async def push_water_spray(request: Request, body: ImageNotificationRequest):
    logger.info(
        f"Received request: {await request.json()}", extra={"project": "water_spray"}
    )
    image_url = (
        f"https://linebot.tunghosteel.com:5003/water_spray_files/{body.image_filename}"
    )
    return _send_notification("water_spray", "water_spray", body.message, image_url)


@router.post("/notify/spark_detection")
@limiter.limit("10/3minute")
async def push_spark_detection(request: Request, body: ImageNotificationRequest):
    logger.info(
        f"Received request: {await request.json()}",
        extra={"project": "spark_detection"},
    )
    image_url = (
        f"https://linebot.tunghosteel.com:5003/spark_detection/{body.image_filename}"
    )
    return _send_notification(
        "spark_detection", "spark_detection", body.message, image_url
    )


@router.post("/notify/dust_detection_150")
@limiter.limit("10/3minute")
async def push_dust_detection(request: Request, body: ImageNotificationRequest):
    logger.info(
        f"Received request: {await request.json()}", extra={"project": "dust_detection"}
    )
    image_url = (
        f"https://linebot.tunghosteel.com:5003/dust_detection_150/{body.image_filename}"
    )
    return _send_notification(
        "dust_detection", "dust_detection", body.message, image_url
    )


@router.post("/notify/pose_detection")
@limiter.limit("10/3minute")
async def push_pose_detection(request: Request, body: TextNotificationRequest):
    logger.info(
        f"Received request: {await request.json()}", extra={"project": "pose_detection"}
    )
    image_url = (
        f"https://linebot.tunghosteel.com:5003/pose_detection?{int(time.time())}"
    )
    return _send_notification(
        "pose_detection", "pose_detection", body.message, image_url
    )
