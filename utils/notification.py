import base64
import requests
from linebot.v3.messaging import PushMessageRequest, TextMessage, ImageMessage
from typing import Optional

from utils.logger import setup_logger
logger = setup_logger(__name__)

class NotificationError(Exception):
    """Custom exception for notification-related errors"""

    def __init__(self, project_name, message):
        self.project_name = project_name
        self.message = message
        super().__init__(f"[{self.project_name}] {self.message}")


def encode_header(value):
    return f"=?utf-8?b?{base64.b64encode(value.encode('utf-8')).decode('utf-8')}?="

def send_to_line_group(
    messaging_api,
    group_id: str,
    text_message: str,
    image_url: Optional[str] = None
) -> None:
    """
    Sends a notification to LINE Group with optional image attachment.

    Args:
        messaging_api: LINE Bot messaging API instance
        group_id (str): Target LINE group ID
        text_message (str): Message to be sent
        image_url (str, optional): URL of the image to be sent

    Raises:
        NotificationError: If message sending fails
    """
    try:
        messages = [TextMessage(text=text_message)]
        if image_url:
            messages.append(
                ImageMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url
                )
            )

        push_message_request = PushMessageRequest(
            to=group_id,
            messages=messages
        )
        messaging_api.push_message(push_message_request)

    except Exception as e:
        raise NotificationError("ty_scrap", str(e)) from e

def send_ntfy_notification(
    ntfy_topic: str,
    text_message: str,
    image_url: Optional[str] = None
) -> None:
    """
    Sends a notification to the NTFY server with an optional image attachment.

    Args:
        ntfy_topic (str): The NTFY topic to send to
        text_message (str): The message to be sent
        image_url (str, optional): URL of image file

    Raises:
        NotificationError: If notification sending fails
    """
    ntfy_url = f"https://thstplsu7001.nttp3.ths.com.tw/{ntfy_topic}"
    
    ntfy_headers = {
        "Title": encode_header(text_message),
        "Tags": "warning"
    }
    
    if image_url:
        ntfy_headers["Attach"] = image_url

    try:
        response = requests.post(
            ntfy_url,
            headers=ntfy_headers,
            verify=False,
            timeout=10
        )
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        raise NotificationError("ty_scrap", str(e)) from e

def send_line_notify(
    line_notify_token: str,
    text_message: str,
    image_url: Optional[str] = None
) -> None:
    """
    Sends a notification to LINE Notify with optional image URL.

    Args:
        line_notify_token (str): LINE Notify authentication token
        text_message (str): Message to be sent
        image_url (str, optional): URL of image to be attached

    Raises:
        NotificationError: If notification sending fails
    """
    notify_url = 'https://notify-api.line.me/api/notify'
    headers = {
        "Authorization": f"Bearer {line_notify_token}"
    }
    
    message = text_message
    if image_url:
        message = f"{text_message}\n{image_url}"
        
    data = {
        "message": message
    }

    try:
        response = requests.post(
            notify_url,
            headers=headers,
            data=data,
            timeout=10
        )
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        raise NotificationError("ty_scrap", str(e)) from e
    
def send_notification(send_func, *args):
        """Generic function to send a notification and handle exceptions."""
        try:
            send_func(*args)
            logger.info(f"{send_func.__name__} sent successfully.")
        except NotificationError as e:
            logger.exception(f"Failed to send notification via {send_func.__name__}: {str(e)}")