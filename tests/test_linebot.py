import os
import base64
import hashlib
import hmac
from fastapi.testclient import TestClient
from main import app
from dotenv import load_dotenv
import os
load_dotenv()


channel_secret = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
client = TestClient(app)

def test_callback():
    body = '{"events":[],"destination":"U000000000000000000000003d9"}'
    hash = hmac.new(channel_secret.encode('utf-8'),
                    body.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(hash)

    response = client.post(
        url="/webhooks/bot/line",
        data=body,
        headers={
            "Content-Type": "application/json",
            'X-Line-Signature': signature.decode('UTF-8')
        })

    assert response.url == 'http://testserver/webhooks/bot/line'
    assert response.status_code == 200
    assert response.json() == 'OK'
