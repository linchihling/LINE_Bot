import os

from .utils import generate_signature

WEBHOOKS_URL = os.getenv("WEBHOOKS_URL_TY_SCRAP")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET_TY_SCRAP")


def test_callback_valid_signature(client):
    """正常情況 - 簽名正確"""
    body_str = '{"events":[],"destination":"U000000000000000000000003d9"}'
    signature = generate_signature(CHANNEL_SECRET, body_str)

    response = client.post(
        url=f"{WEBHOOKS_URL}/line",
        content=body_str,
        headers={"Content-Type": "application/json", "X-Line-Signature": signature},
    )

    assert response.status_code == 200


def test_callback_invalid_signature(client):
    """異常情況 - 簽名錯誤"""
    body_str = '{"events":[],"destination":"U000000000000000000000003d9"}'
    signature = "invalid_signature"

    response = client.post(
        url=f"{WEBHOOKS_URL}/line",
        content=body_str,
        headers={"Content-Type": "application/json", "X-Line-Signature": signature},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Invalid signature"}
