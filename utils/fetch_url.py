import requests
from bs4 import BeautifulSoup
from typing import List, Optional

from utils.factory import setup_logger

logger = setup_logger(__name__)

_HTML_PARSER = "html.parser"
_PNG_EXTENSION = ".png"


def _fetch_html_soup(url: str) -> Optional[BeautifulSoup]:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, _HTML_PARSER)
    except requests.RequestException as exc:
        logger.error(f"Failed to fetch {url}: {exc}", extra={"project": "fetch_folder"})
        return None


def fetch_last_5_images(machine: str) -> List[str]:
    """
    Retrieves the latest 5 image_paths from the machine
    Example: "20241023_10/2024-10-23_10_01_21_63_900_D25.png"
    """
    endpoint_map = {
        "rl1": "https://rebar-detection-sec1-ty.tunghosteel.com/get_last_5_images",
        "rl2": "https://rebar-detection-sec2-ty.tunghosteel.com/get_last_5_images",
    }

    url = endpoint_map.get(machine)
    if not url:
        logger.warning(
            f"Unknown machine identifier: {machine}", extra={"project": "fetch_folder"}
        )
        return []

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        latest_5_images = [
            item.get("path", "").lstrip("/static/images/") for item in data
        ]
        logger.info(
            f"{machine} fetched latest 5 images: {latest_5_images}",
            extra={"project": "fetch_folder"},
        )
        return latest_5_images
    except requests.RequestException as exc:
        logger.error(
            f"Failed to fetch images from {url}: {exc}",
            extra={"project": "fetch_folder"},
        )
        return []


def fetch_folder_links(url: str) -> List[str]:
    soup = _fetch_html_soup(url)
    if soup is None:
        logger.warning(
            "Failed to retrieve HTML content.", extra={"project": "fetch_folder"}
        )
        return []

    return [
        link.get("href")
        for link in soup.find_all("a")
        if link.get("href", "").endswith("/")
    ]


def fetch_image_names(url: str) -> List[str]:
    soup = _fetch_html_soup(url)
    if soup is None:
        logger.warning(
            "Failed to retrieve HTML content.", extra={"project": "fetch_image"}
        )
        return []

    return [link.get("href") for link in soup.find_all("a") if link.get("href")]


def fetch_latest_png_images(directory_url: str, max_images: int = 6) -> List[str]:
    soup = _fetch_html_soup(directory_url)
    if soup is None:
        return []

    png_links = [
        link.get("href")
        for link in soup.find_all("a")
        if link.get("href", "").endswith(_PNG_EXTENSION)
    ]
    return [directory_url + img for img in png_links[-max_images:]]
