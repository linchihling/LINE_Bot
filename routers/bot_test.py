from fastapi import APIRouter, Request, Header
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    Configuration,
    ApiClient,
    MessagingApi,
    ShowLoadingAnimationRequest,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent
import traceback
import os
from logger import setup_logger
from utils.member_status import get_member_status, load_members, save_members

logger = setup_logger("bot_test", "logs/bot_test.log")

# Initialize the LINE API Client
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN_2'))
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET_2'))
webhooks_url = os.getenv('WEBHOOKS_URL_TEST')

members = load_members()
router = APIRouter(
    prefix=webhooks_url,
    tags=["test"],
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


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    message = event.message.text
    token = event.reply_token
    user_id = event.source.user_id
    if get_member_status(messaging_api, event, logger):
        members = load_members()
        logger.info(f"User: {members[user_id]}, message: {message}")
        show_loading_animation_request = ShowLoadingAnimationRequest(
            chat_id=user_id, loadingSeconds=5
        )
        messaging_api.show_loading_animation(show_loading_animation_request)
        try:
            reply_message = ReplyMessageRequest(
                reply_token=token, 
                messages=[TextMessage(text=message)]
            )
            messaging_api.reply_message(reply_message)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"User: {user_id}, Error: {str(e)}")
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