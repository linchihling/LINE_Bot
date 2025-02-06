import requests
from utils.image_utils import encode_header
import logging

logger = logging.getLogger(__name__)

def send_ntfy_notification(ntfy_topic: str, text_message: str, image_path: str):
    """
    Sends a notification to the NTFY server with an optional image attachment.

    :param text_message: The message to be sent.
    :param image_path: The path to the image file.
    """
    ntfy_url = f"https://thstplsu7001.nttp3.ths.com.tw/{ntfy_topic}"

    ntfy_headers = {
        "Title": encode_header(text_message),  
        "Filename": encode_header(image_path.split("/")[-1]),
        "Tags": "warning"
    }

    try:
        with open(image_path, "rb") as file:
            response = requests.post(ntfy_url, data=file, headers=ntfy_headers, verify=False)
    except FileNotFoundError:
        logger.error(f"File {image_path} not found.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")

    return {"status": response.status_code, "message": response.text}