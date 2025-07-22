import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# 基本設定
base_url = "https://cve.ntnu.edu.tw/"
keywords = ["課程資訊"]
visited_urls = set()  # 紀錄已訪問的網址
found_results = []    # 紀錄找到的內容

# 搜尋關鍵字的函式
def search_keywords(url, keywords):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 搜尋網頁內容是否包含關鍵字
        text = soup.get_text()
        for keyword in keywords:
            if keyword in text:
                found_results.append((url, keyword))

        # 爬取所有內部連結
        links = soup.find_all("a", href=True)
        for link in links:
            full_url = urljoin(base_url, link['href'])
            if full_url.startswith(base_url) and full_url not in visited_urls:
                visited_urls.add(full_url)
                search_keywords(full_url, keywords)
    except Exception as e:
        print(f"Error accessing {url}: {e}")

# 開始爬取
visited_urls.add(base_url)
search_keywords(base_url, keywords)

# 顯示結果
if found_results:
    print("找到以下關鍵字：")
    for result in found_results:
        print(f"網址: {result[0]}, 關鍵字: {result[1]}")
else:
    print("未找到相關關鍵字。")
