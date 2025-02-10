import base64
import requests
import os
import datetime

from utils.setting import setup_logger

logger = setup_logger(__name__)

def download_image(image_url, project_dir):
    """
    Downloads an image from the given URL and saves it locally.
    
    :param image_url: The URL of the image to download.
    :param save_path: The local path to save the image.
    :return: True if download is successful, otherwise False.
    """
    os.makedirs(project_dir, exist_ok=True)
    # today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    # save_dir = os.path.join(project_dir, today_date)
    save_path = os.path.join(project_dir,  os.path.basename(image_url))
    try:
        response = requests.get(image_url, stream=True, verify=False)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            logger.info(f"Successfully downloaded image: {image_url}")
            return save_path  # Return the saved file path
        else:
            logger.error(f"{response.status_code} Failed to download image: {image_url}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None

def encode_header(value):
    return f"=?utf-8?b?{base64.b64encode(value.encode('utf-8')).decode('utf-8')}?="