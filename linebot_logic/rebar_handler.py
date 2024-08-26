from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
    StickerMessage,
)
import traceback
import requests
import json
from utils.member_status import get_member_status, load_members, save_members

def process_image_request(event, logger, messaging_api):
    members = load_members()
    message = event.message.text
    side = message[1:]
    token = event.reply_token
    client_id = event.source.user_id
    url = f"https://linebot.tunghosteel.com:5003/api/v1/get_photos/{side}"
    data = requests.get(url, verify=False).json()
    base_url = data['base_url']
    images_name = data['images_name']
    img_urls = [f"{base_url}/{img}" for img in images_name]
    logger.info(f"User: {members[client_id]}, message: {message}, Image names: {images_name}")
    image_message = [
        ImageMessage(original_content_url=img_url, preview_image_url=img_url)
        for img_url in img_urls
    ]

    if not image_message:
        error_message = TextMessage(text="Image not found, please try again later.")
        reply_imgs = ReplyMessageRequest(reply_token=token, messages=[error_message])
    else:
        reply_imgs = ReplyMessageRequest(reply_token=token, messages=image_message)

    messaging_api.reply_message(reply_imgs)

def handle_text_message(event, logger, messaging_api):
    message = event.message.text
    token = event.reply_token
    client_id = event.source.user_id

    if get_member_status(messaging_api, event, logger):
        try:
            if message == "!ab" or message == "!cd":
                process_image_request(event, logger, messaging_api)
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
        logger.info(f"User: {client_id}, message: {message}")

def handle_follow(event, messaging_api):
    user_id = event.source.user_id
    sticker_message = StickerMessage(package_id="6370", sticker_id="11088021")
    messaging_api.push_message(
        user_id, messages=[TextMessage(text="功能選單觀看即時影像"), sticker_message]
    )
    logger.info(f"New follower: {user_id}")
