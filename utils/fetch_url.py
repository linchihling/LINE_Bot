import requests
from bs4 import BeautifulSoup
from typing import List

from utils.logger import setup_logger

logger = setup_logger(__name__)
HTML_PARSER = "html.parser"
PNG_EXTENSION = ".png"


def fetch_html_soup(url: str) -> BeautifulSoup:
    """
    發送請求並返回解析後的 BeautifulSoup 對象。
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, HTML_PARSER)
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}", extra={"project": "fetch_folder"})
        return None


def fetch_last_5_images(machine: str) -> List[str]:
    """
    從軋一/軋二電腦擷取最新 5 張影像的路徑名稱
    例如:latest_5_images[0] = "20241023_10/2024-10-23_10_01_21_63_900_D25.png"
    """
    if machine == "rl1":
        url = "https://rebar-detection-sec1-ty.tunghosteel.com/get_last_5_images"
    elif machine == "rl2":
        url = "https://rebar-detection-sec2-ty.tunghosteel.com/get_last_5_images"
    else:
        return []
    response = requests.get(url, timeout=10).json()

    latest_5_images = [path.get("path").lstrip("/static/images/") for path in response]
    logger.info(
        f"{machine} successfully fetched the latest 5 images: {latest_5_images}",
        extra={"project": "fetch_folder"},
    )

    return latest_5_images


def fetch_folder_links(url: str) -> List[str]:
    """
    獲取給定 URL 中的所有資料夾鏈接。
    """
    soup = fetch_html_soup(url)
    if soup is None:
        logger.warning(
            "Failed to retrieve HTML content.", extra={"project": "fetch_folder"}
        )
        return []

    folder_links = [
        link.get("href")
        for link in soup.find_all("a")
        if link.get("href").endswith("/")
    ]
    return folder_links


def fetch_image_names(url: str) -> List[str]:
    """
    獲取給定 URL 中的所有圖片鏈接。
    """
    soup = fetch_html_soup(url)
    if soup is None:
        logger.warning(
            "Failed to retrieve HTML content.", extra={"project": "fetch_image"}
        )
        return []

    image_names = [link.get("href") for link in soup.find_all("a") if link.get("href")]
    return image_names


def fetch_latest_png_images(directory_url: str, max_images: int = 6) -> List[str]:
    """
    獲取給定資料夾 URL 中最新的 PNG 圖片鏈接。
    """
    soup = fetch_html_soup(directory_url)
    if soup is None:
        return []

    png_links = [
        link.get("href")
        for link in soup.find_all("a")
        if link.get("href").endswith(PNG_EXTENSION)
    ]
    latest_png_links = png_links[-max_images:]
    return [directory_url + img for img in latest_png_links]
