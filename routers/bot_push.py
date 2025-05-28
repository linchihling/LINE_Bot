import os
import time
from pydantic import BaseModel
from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from linebot.v3 import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent  # noqa F401
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
    send_notification,
)
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize the LINE API Client
configuration = Configuration(
    access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN_PUSHBOT")
)
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET_PUSHBOT"))
WEBHOOKS_URL = os.getenv("WEBHOOKS_URL_PUSHBOT")
group_id_push_ty = os.getenv("GROUP_ID_PUSHBOT_TY_SCRAP")
group_id_ty_water_spray = os.getenv("GROUP_ID_PUSHBOT_TY_WATER_SPRAY")
group_id_ty_spark_detection = os.getenv("GROUP_ID_PUSHBOT_TY_SPARK_DETECTION")
group_id_ty_dust_detection = os.getenv("GROUP_ID_PUSHBOT_TY_DUST_DETECTION")
group_id_ty_pose_detection = os.getenv("GROUP_ID_PUSHBOT_TY_POSE_DETECTION")
line_notify_token = os.getenv("LINE_NOTIFY_TOKEN")
ntfy_ty_scrap = os.getenv("NTFY_TY_SCRAP")
ntfy_ty_water_spray = os.getenv("NTFY_TY_WATER_SPRAY")
ntfy_ty_spark_detection = os.getenv("NTFY_TY_SPARK_DETECTION")
ntfy_ty_dust_detection = os.getenv("NTFY_TY_DUST_DETECTION")
ntfy_ty_pose_detection = os.getenv("NTFY_TY_POSE_DETECTION")

# Limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=WEBHOOKS_URL,
    tags=["bot_push"],
    responses={404: {"description": "Not found"}},
)


def limit_error():
    logger.warning(
        "Rate limit triggered during LINE webhook", extra={"project": "line"}
    )
    return 1


@router.post("/line")
@limiter.limit("5/minute", error_message=limit_error)
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


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    message = event.message.text
    group_id = event.source.group_id
    if message == "(系統測試，請忽略)":
        logger.info(
            f"Replied with Group ID: {group_id} (from {event.source.user_id})",
            extra={"project": "line"},
        )


class ScrapNotificationRequest(BaseModel):
    rolling_line: str
    message: str
    image_path: str


class ImageNotificationRequest(BaseModel):
    message: str
    image_filename: str


class TextNotificationRequest(BaseModel):
    message: str


@router.post("/notify/ty_scrap")
@limiter.limit("10/3minute")
async def push_message(request: Request, request_body: ScrapNotificationRequest):
    logger.info(
        f"Received request: {await request.json()}", extra={"project": "ty_scrap"}
    )
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

        return {"status": "success", "message": "Notification sent successfully"}

    except Exception as e:
        logger.error(
            f"Error in push_message: {str(e)}",
            exc_info=True,
            extra={"project": "ty_scrap"},
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/notify/water_spray")
@limiter.limit("10/3minute")
async def push_message_water_spray(
    request: Request, request_body: ImageNotificationRequest
):

    logger.info(
        f"Received request: {await request.json()}", extra={"project": "water_spray"}
    )
    text_message = request_body.message
    image_filename = request_body.image_filename
    image_url = (
        f"https://linebot.tunghosteel.com:5003/water_spray_files/{image_filename}"
    )
    try:
        # Push message to Line Group
        send_notification(
            "water_spray",
            send_to_line_group,
            messaging_api,
            group_id_ty_water_spray,
            text_message,
            image_url,
        )
        # NTFY Notification
        send_notification(
            "water_spray",
            send_ntfy_notification,
            ntfy_ty_water_spray,
            text_message,
            image_url,
        )
        return {"status": "success", "message": "Notification sent successfully"}

    except Exception as e:
        logger.error(
            f"Error in push_message: {str(e)}",
            exc_info=True,
            extra={"project": "water_spray"},
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/notify/spark_detection")
@limiter.limit("10/3minute")
async def push_message_spark_detection(
    request: Request, request_body: ImageNotificationRequest
):

    logger.info(
        f"Received request: {await request.json()}",
        extra={"project": "spark_detection"},
    )
    text_message = request_body.message
    image_filename = request_body.image_filename
    image_url = f"https://linebot.tunghosteel.com:5003/spark_detection/{image_filename}"
    try:
        # Push message to Line Group
        send_notification(
            "spark_detection",
            send_to_line_group,
            messaging_api,
            group_id_ty_spark_detection,
            text_message,
            image_url,
        )
        # NTFY Notification
        send_notification(
            "spark_detection",
            send_ntfy_notification,
            ntfy_ty_spark_detection,
            text_message,
            image_url,
        )
        return {"status": "success", "message": "Notification sent successfully"}

    except Exception as e:
        logger.error(
            f"Error in push_message: {str(e)}",
            exc_info=True,
            extra={"project": "spark_detection"},
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/notify/dust_detection_150")
@limiter.limit("10/3minute")
async def push_message_dust_detection(
    request: Request, request_body: ImageNotificationRequest
):

    logger.info(
        f"Received request: {await request.json()}", extra={"project": "dust_detection"}
    )
    text_message = request_body.message
    image_filename = request_body.image_filename
    image_url = (
        f"https://linebot.tunghosteel.com:5003/dust_detection_150/{image_filename}"
    )
    try:
        # Push message to Line Group
        send_notification(
            "dust_detection",
            send_to_line_group,
            messaging_api,
            group_id_ty_dust_detection,
            text_message,
            image_url,
        )
        # NTFY Notification
        send_notification(
            "dust_detection",
            send_ntfy_notification,
            ntfy_ty_dust_detection,
            text_message,
            image_url,
        )
        return {"status": "success", "message": "Notification sent successfully"}

    except Exception as e:
        logger.error(
            f"Error in push_message: {str(e)}",
            exc_info=True,
            extra={"project": "dust_detection"},
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/notify/pose_detection")
@limiter.limit("10/3minute")
async def push_message_pose_detection(
    request: Request, request_body: TextNotificationRequest
):

    logger.info(
        f"Received request: {await request.json()}", extra={"project": "pose_detection"}
    )
    text_message = request_body.message
    date_time = time.time()
    image_url = f"https://linebot.tunghosteel.com:5003/pose_detection?{date_time}"
    try:
        # Push message to Line Group
        send_notification(
            "pose_detection",
            send_to_line_group,
            messaging_api,
            group_id_ty_pose_detection,
            text_message,
            image_url,
        )
        # NTFY Notification
        send_notification(
            "pose_detection",
            send_ntfy_notification,
            ntfy_ty_pose_detection,
            text_message,
            image_url,
        )
        return {"status": "success", "message": "Notification sent successfully"}

    except Exception as e:
        logger.error(
            f"Error in push_message: {str(e)}",
            exc_info=True,
            extra={"project": "pose_detection"},
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")
