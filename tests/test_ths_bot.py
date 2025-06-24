from unittest.mock import patch

import os
from .utils import generate_signature

WEBHOOKS_URL = os.getenv("WEBHOOKS_URL_PUSHBOT")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET_PUSHBOT")


def test_callback(client):
    body_str = '{"events":[],"destination":"U000000000000000000000003d9"}'
    signature = generate_signature(LINE_CHANNEL_SECRET, body_str)

    response = client.post(
        url=f"{WEBHOOKS_URL}/line",
        content=body_str,
        headers={"Content-Type": "application/json", "X-Line-Signature": signature},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


def test_push_message_success(client):
    payload = {"rolling_line": "1", "message": "Test Message", "image_path": "test.png"}

    with patch("routers.ths_bot.send_notification") as mock_send:
        mock_send.return_value = None
        response = client.post(f"{WEBHOOKS_URL}/notify/ty_scrap", json=payload)

        assert response.status_code == 200
        assert response.json() == {
            "status": "success",
            "message": "Notification sent successfully",
        }
