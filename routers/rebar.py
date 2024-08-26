from fastapi import APIRouter, Request, Header
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
    StickerMessage,
    Configuration,
    ApiClient,
    MessagingApi,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent
import traceback
import os
import requests
import json

from logger import setup_logger
logger = setup_logger("rebar", "logs/rebar.log")

from linebot_logic.member_status import get_member_status
with open('members.json', 'r') as file:
    members = json.load(file)

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
    return 'OK'

def process_image_request(side, token, client_id, members):
    url = f"https://linebot.tunghosteel.com:5003/api/v1/get_photos/{side}"
    data = requests.get(url, verify=False).json()
    base_url = data['base_url']
    images_name = data['images_name']
    img_urls = [f"{base_url}/{imUser: {members[client_id]}g}" for img in images_name]
    logger.info(f", Directory URL: {img_urls}")
    image_message = [
        ImageMessage(original_content_url=img_url, preview_image_url=img_url)
        for img_url in img_urls
    ]
    reply_imgs = ReplyMessageRequest(reply_token=token, messages=image_message)
    messaging_api.reply_message(reply_imgs)


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    message = event.message.text
    token = event.reply_token
    client_id = event.source.user_id

    if get_member_status(members, logger, client_id):
        try:
            if message == "!ab" or message == "!cd":
                side = message[1:]
                process_image_request(side, token, client_id, members)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error: {str(e)}")
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=token,
                    messages=[TextMessage(text="Unable to process your request")],
                )
            )
    else:
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=token,
                messages=[TextMessage(text="You are not a member, please contact the developer.")],
            )
        )
        logger.info(f"User: {user_id}, message: {message}")

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(router, host="0.0.0.0", port=6000)


