import base64
import requests
from linebot.v3.messaging import PushMessageRequest, TextMessage, ImageMessage
from typing import Optional

from utils.logger import setup_logger

logger = setup_logger(__name__)


def encode_header(value):
    return f"=?utf-8?b?{base64.b64encode(value.encode('utf-8')).decode('utf-8')}?="


def send_to_line_group(
    messaging_api, group_id: str, text_message: str, image_url: Optional[str] = None
) -> None:
    """
    Sends a notification to LINE Group with optional image attachment.

    Args:
        messaging_api: LINE Bot messaging API instance
        group_id (str): Target LINE group ID
        text_message (str): Message to be sent
        image_url (str, optional): URL of the image to be sent

    """
    try:
        messages = [TextMessage(text=text_message)]
        if image_url:
            messages.append(
                ImageMessage(
                    original_content_url=image_url, preview_image_url=image_url
                )
            )

        push_message_request = PushMessageRequest(to=group_id, messages=messages)
        messaging_api.push_message(push_message_request)

    except Exception as e:
        raise Exception(str(e))


def send_ntfy_notification(
    ntfy_topic: str, text_message: str, image_url: Optional[str] = None
) -> None:
    """
    Sends a notification to the NTFY server with an optional image attachment.

    Args:
        ntfy_topic (str): The NTFY topic to send to
        text_message (str): The message to be sent
        image_url (str, optional): URL of image file

    """
    ntfy_url = f"https://thstplsu7001.nttp3.ths.com.tw/{ntfy_topic}"

    ntfy_headers = {"Title": encode_header(text_message), "Tags": "warning"}

    if image_url:
        ntfy_headers["Attach"] = image_url

    try:
        response = requests.post(
            ntfy_url, headers=ntfy_headers, verify=False, timeout=10  # nosec B501
        )
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise Exception(str(e))


def send_notification(project_name, send_func, *args):
    """Generic function to send a notification and handle exceptions."""
    try:
        send_func(*args)
        logger.info(
            f"{send_func.__name__} sent successfully.", extra={"project": project_name}
        )
    except Exception as e:
        logger.error(
            f"Failed to send notification via {send_func.__name__}: {str(e)}",
            extra={"project": project_name},
        )
