import base64
import hashlib
import hmac


def generate_signature(secret: str, body: str) -> str:
    """
    產生X-Line-Signature給LINE webhook
    """
    hash = hmac.new(
        secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
    ).digest()
    return base64.b64encode(hash).decode("utf-8")
