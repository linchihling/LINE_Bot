from fastapi import APIRouter, Request, Header
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    Configuration,
    ApiClient,
    MessagingApi
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logger import setup_logger

logger = setup_logger("bot_test", "logs/bot_test.log")

# Initialize the LINE API Client
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN_3'))
api_client = ApiClient(configuration=configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET_3'))
webhooks_url = os.getenv('WEBHOOKS_URL_TEST')

router = APIRouter(
    prefix=webhooks_url,
    tags=["test"],
    responses={404: {"description": "Not found"}},
)

# 公司郵箱域名
COMPANY_DOMAIN = "tunghosteel.com"

# 存儲待驗證的用戶信息
pending_verifications = {}

# 存儲已驗證的用戶
authorized_users = set()

def is_company_email(email):
    return email.lower().endswith(f"@{COMPANY_DOMAIN}")

def generate_verification_code():
    return ''.join(random.choices('0123456789', k=6))

def send_verification_email(email, code):
    sender_email = "chihling870916@gmail.com"
    sender_password = "ohhv xzwr nmbv bcml"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = "LINE Bot Verification Code"

    body = f"Your verification code is: {code}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())

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
    user_id = event.source.user_id
    message = event.message.text
    token = event.reply_token

    if user_id in authorized_users:
        reply_text = f"已驗證用戶的消息：{message}"
    elif user_id in pending_verifications:
        # 檢查驗證碼
        if message == pending_verifications[user_id]['code']:
            authorized_users.add(user_id)
            del pending_verifications[user_id]
            reply_text = "驗證成功！你現在可以使用 LINE Bot 了。"
        else:
            reply_text = "驗證碼錯誤，請重試。"
    elif re.match(r"[^@]+@[^@]+\.[^@]+", message):  
      
        if is_company_email(message):
            code = generate_verification_code()
            pending_verifications[user_id] = {'email': message, 'code': code}
            send_verification_email(message, code)
            reply_text = "驗證碼已發送到你的郵箱，請查收並輸入。"
        else:
            reply_text = "請使用公司郵箱地址。"
    else:
        reply_text = "請發送你的公司郵箱地址進行驗證。"

    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=token,
            messages=[TextMessage(text=reply_text)]
        )
    )

    logger.info(f"User: {user_id}, message: {message}")