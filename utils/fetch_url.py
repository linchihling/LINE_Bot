import requests
from bs4 import BeautifulSoup
from typing import List

HTML_PARSER = 'html.parser'
PNG_EXTENSION = '.png'

def fetch_html_soup(url: str) -> BeautifulSoup:
    """
    發送請求並返回解析後的 BeautifulSoup 對象。
    """
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()  
        return BeautifulSoup(response.text, HTML_PARSER)
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def fetch_folder_links(url: str) -> List[str]:
    """
    獲取給定 URL 中的所有資料夾鏈接。
    """
    soup = fetch_html_soup(url)
    if soup is None:
        return []
    
    folder_links = [link.get('href') for link in soup.find_all('a') if link.get('href').endswith('/')]
    return folder_links

def fetch_image_names(url: str) -> List[str]:
    """
    獲取給定 URL 中的所有圖片鏈接。
    """
    soup = fetch_html_soup(url)
    if soup is None:
        return []
    
    image_names = [link.get('href') for link in soup.find_all('a') if link.get('href')]
    return image_names

def fetch_latest_directory(url: str) -> str:
    """
    獲取給定 URL 中最新的資料夾 URL。
    """
    soup = fetch_html_soup(url)
    if soup is None:
        return ""
    
    folder_links = [link.get('href') for link in soup.find_all('a') if link.get('href').endswith('/')]
    if not folder_links:
        return ""
    
    latest_directory = folder_links[-1]
    return url + latest_directory

def fetch_latest_png_images(directory_url: str, max_images: int = 6) -> List[str]:
    """
    獲取給定資料夾 URL 中最新的 PNG 圖片鏈接。
    """
    soup = fetch_html_soup(directory_url)
    if soup is None:
        return []
    
    png_links = [link.get('href') for link in soup.find_all('a') if link.get('href').endswith(PNG_EXTENSION)]
    latest_png_links = png_links[-max_images:]
    return [directory_url + img for img in latest_png_links]
