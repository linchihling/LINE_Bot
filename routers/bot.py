from pydantic import BaseModel
from fastapi import APIRouter, Request, Header, HTTPException
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
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent
from linebot_logic.bot_handler import handle_text_message, handle_follow
import os

# Initialize the LINE API Client
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
webhooks_url = os.getenv('WEBHOOKS_URL_BOT')


router = APIRouter(
    prefix=webhooks_url,
    tags=["bot"],
    responses={404: {"description": "Not found"}},
)

@router.post("/line")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        # raise HTTPException(status_code=400, detail="chatbot handle body error.")
        pass
    return 'OK'

GROUP_ID = "C1bf5730422b6f1cd42eed7ad1359a8f0"

class NotifyRequest(BaseModel):
    rolling_line: str
    message: str
    image_path: str

@router.post("/notify")
async def push_message(request_body: NotifyRequest):
    try:
        # request data
        rolling_line = request_body.rolling_line
        text_message = request_body.message
        img_path = request_body.image_path
        
        # push
        image_path = f"https://linebot.tunghosteel.com:5003/rl{rolling_line}/{img_path}"
        push_message_request = PushMessageRequest(
            to=GROUP_ID,
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
    handle_text_message(event, messaging_api)

@handler.add(FollowEvent)
def handle_follow_event(event):
    handle_follow(event, messaging_api)
