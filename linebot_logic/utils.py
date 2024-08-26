import requests
from bs4 import BeautifulSoup
def fetch_folder_links(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 找到所有的資料夾鏈接
    folder_links = [link.get('href') for link in soup.find_all('a') if link.get('href').endswith('/')]
   
    return folder_links

def fetch_image_names(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 找到所有的資料夾鏈接
    image_names = [link.get('href') for link in soup.find_all('a') if link.get('href')]
   
    return image_names

def fetch_latest_directory(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 找到所有的資料夾鏈接
    folder_links = [link.get('href') for link in soup.find_all('a') if link.get('href').endswith('/')]
    # 資料夾以日期排序，最新的資料夾會在最後
    latest_directory = folder_links[-1]
    return url + latest_directory  # 返回完整的最新資料夾 URL

def fetch_latest_png_images(directory_url, max_images=6):
    response = requests.get(directory_url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 找到所有的 png 圖片鏈接
    png_links = [link.get('href') for link in soup.find_all('a') if link.get('href').endswith('.png')]
    # 取最新的 max_images 張圖片
    latest_png_links = png_links[-max_images:]
    return [directory_url + img for img in latest_png_links]  # 返回完整的圖片 URL