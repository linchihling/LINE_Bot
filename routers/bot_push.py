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
import os
import requests
from slowapi import Limiter
from slowapi.util import get_remote_address

from utils.image_utils import download_image
from utils.ntfy import send_ntfy_notification
from setting import setup_logger 

logger = setup_logger("bot_push")

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
        # image_url = "https://rm-44.fucosteel.com.vn/images/2024-08-24/F403660106_result.jpg"
    except Exception as e:
        print(f"Error request data: {e}")
        raise HTTPException(status_code=500, detail="Failed to request data.")
    
    # Push message to Line
    try:
        push_message_request = PushMessageRequest(
            to=group_id_push_ty,
            messages=[
                TextMessage(text=text_message),
                ImageMessage(original_content_url=image_url, preview_image_url=image_url),
            ]
        )
        messaging_api.push_message(push_message_request)
        logger.info("Push message sent to Line successfully.")
    
    except Exception as e:
        logger.info(f"Error pushing message to Line: {e}")
        raise HTTPException(status_code=500, detail="Failed to send Line message.")
    
    # NTFY Notification
    try:
        save_dir = "ntfy/ty_scrap"
        image_path = os.path.join(save_dir,  os.path.basename(image_url))
        _ = download_image(image_url, save_dir)
        send_ntfy_notification(ntfy_topic, text_message, image_path)

    except Exception as e:
        logger.info(f"Error sending NTFY notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send ntfy notification.")
    
    
    # LINE Notify
    try:
        notify_url = 'https://notify-api.line.me/api/notify'
        headers = {
            'Authorization': 'Bearer ' + line_notify_token    # 設定權杖
        }
        data = {
            'message': f"{text_message}\n{image_url}"
        }
        response = requests.post(notify_url, headers=headers, data=data)
        if response.status_code == 200:
            logger.info("Notifications sent successfully.")
        else:
            logger.error(f"Failed to send notification: {response.status_code} - {response.text}")

    except Exception as e:
        logger.exception("An error occurred while sending the LINE notification.")






# @router.post("/notify/project2")
# @limiter.limit("10/hour")
# async def push_message(request: Request, request_body: NotifyRequest):
#     try:
#         # request data
#         rolling_line = request_body.rolling_line
#         text_message = request_body.message
#         img_path = request_body.image_path
        
#         # push
#         image_path = f"https://linebot.tunghosteel.com:5003/rl{rolling_line}/{img_path}"
#         push_message_request = PushMessageRequest(
#             to=group_id_push_project2,
#             messages=[
#                 TextMessage(text=text_message),
#                 ImageMessage(original_content_url=image_path, preview_image_url=image_path),
#             ]
#         )
#         messaging_api.push_message(push_message_request)

#     except Exception as e:
#         print(f"Error pushing message: {e}")
#         raise HTTPException(status_code=500, detail="Failed to send push message.")
    
#     return {"message": "Push message sent successfully."}


@router.post("/notify/ntfy_test")
@limiter.limit("100/hour")
async def push_message(request: Request, request_body: NotifyRequest):
    
    try:
        rolling_line = request_body.rolling_line
        text_message = request_body.message
        img_path = request_body.image_path
        
        # image_url = f"https://linebot.tunghosteel.com:5003/rl{rolling_line}/{img_path}"
        image_url = "https://rm-44.fucosteel.com.vn/images/2024-08-24/F403660106_result.jpg"
    except Exception as e:
        print(f"Error request data: {e}")
        raise HTTPException(status_code=500, detail="Failed to request data.")
    
    # NTFY Notification
    try:
        image_path = os.path.join("ntfy", image_url.split("/")[-1])
        _ = download_image(image_url, image_path)
        send_ntfy_notification(text_message, image_path)

    except Exception as e:
        logger.info(f"Error sending NTFY notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send ntfy notification.")

    
    
    return {"message": "Push message sent successfully."}

