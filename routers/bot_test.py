from typing import List, Optional

from fastapi import APIRouter, HTTPException, Header, Request, Depends
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextMessage, MessageEvent, TextSendMessage, StickerMessage, \
    StickerSendMessage
from pydantic import BaseModel
from dependencies import get_token_header


LINE_CHANNEL_ACCESS_TOKEN = "PNTQ48ZPiiWOv0YBbsbBRJ2ZzdlZD719spRZKFChQEP0M8e7E4oIu0N3tqF8kOL+qbDMoKmk496hYchNI+Q7JnujrsK5K7nwssAcUdMj2qQnzSxuKaY3CSEsHS7xE0sgrPMOtDSCtvfLaLeTC04BNgdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "96a02726d0ec48f68b50696deaaa9184"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

router = APIRouter(
    prefix="/webhooks/test",
    tags=["test"],
    responses={404: {"description": "Not found"}},
)

# router = APIRouter()

class Line(BaseModel):
    destination: str
    events: list


@router.post("/line")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="chatbot handle body error.")
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    print("!!!!!!!!!!!!!!!!!!!!!!")
    print(event)
    print("!!!!!!!!!!!!!!!!!!!!!!")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )


@handler.add(MessageEvent, message=StickerMessage)
def sticker_text(event):
    # Judge condition
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(package_id='6136', sticker_id='10551379')
    )