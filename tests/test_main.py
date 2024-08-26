import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_bot_webhook():
    headers = {
        "X-Line-Signature": "test_signature"
    }
    body = {
        "events": [
            {
                "type": "message",
                "replyToken": "test_reply_token",
                "source": {
                    "userId": "test_user_id",
                    "type": "user"
                },
                "message": {
                    "id": "test_message_id",
                    "type": "text",
                    "text": "Hello"
                }
            }
        ]
    }
    
    response = client.post("/bot/callback", headers=headers, json=body)
    assert response.status_code == 200
    assert response.text == "OK"

def test_bot2_webhook():
    headers = {
        "X-Line-Signature": "test_signature"
    }
    body = {
        "events": [
            {
                "type": "message",
                "replyToken": "test_reply_token",
                "source": {
                    "userId": "test_user_id",
                    "type": "user"
                },
                "message": {
                    "id": "test_message_id",
                    "type": "text",
                    "text": "Hello"
                }
            }
        ]
    }
    
    response = client.post("/bot_test/callback", headers=headers, json=body)
    assert response.status_code == 200
    assert response.text == "OK"
