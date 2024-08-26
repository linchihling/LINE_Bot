from fastapi import APIRouter, Request, Header
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
    Configuration,
    ApiClient,
    MessagingApi,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import traceback
import os
import requests
from logger import setup_logger

logger = setup_logger("rebar_logger", "logs/rebar.log")

# Initialize the LINE API Client
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN_3'))
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET_3'))

router = APIRouter(
    prefix="/webhooks/rebar",
    tags=["rebar"],
    responses={404: {"description": "Not found"}},
)

@router.post("/line")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        logger.error("Invalid signature error")
        pass
    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    message = event.message.text
    token = event.reply_token
    client_id = event.source.user_id

    if message:
        try:
            if message == "!ab":
                url = "https://linebot.tunghosteel.com:5003/api/v1/get_photos/ab"
                data = requests.get(url, verify=False).json()
                base_url = data['base_url']
                images_name = data['images_name']
                img_urls = [base_url + "/" + img for img in images_name]
                logger.info(f"Client ID: {client_id}, Directory URL: {img_urls}")
                image_message = [
                    ImageMessage(original_content_url=img_url, preview_image_url=img_url)
                    for img_url in img_urls
                ]
                reply_imgs = ReplyMessageRequest(reply_token=token, messages=image_message)
                messaging_api.reply_message(reply_imgs)
            elif message == "!cd":
                url = "https://linebot.tunghosteel.com:5003/api/v1/get_photos/cd"
                data = requests.get(url, verify=False).json()
                base_url = data['base_url']
                images_name = data['images_name']
                img_urls = [base_url + "/" + img for img in images_name]
                logger.info(f"Client ID: {client_id}, Directory URL: {img_urls}")
                image_message = [
                    ImageMessage(original_content_url=img_url, preview_image_url=img_url)
                    for img_url in img_urls
                ]
                reply_imgs = ReplyMessageRequest(reply_token=token, messages=image_message)
                messaging_api.reply_message(reply_imgs)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error: {str(e)}")
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=token,
                    messages=[TextMessage(text="Unable to process your request")],
                )
            )