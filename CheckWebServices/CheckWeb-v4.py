import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

# 主網址與關鍵字
base_url = "https://www.ntnu.edu.tw/president/"
keywords = ["吳正己"]

# 已訪問的網址集合
visited_urls = set()

# 紀錄進度
checked_count = 0
found_keywords = []

def crawl(url):
    global checked_count
    try:
        # 正規化 URL
        normalized_url = re.sub(r'#.*', '', url)
        if normalized_url in visited_urls:
            return
        visited_urls.add(normalized_url)
        checked_count += 1
        print(f"[進度] 正在檢查: {normalized_url}")
        
        # 發送 HTTP GET 請求
        response = requests.get(normalized_url, timeout=10)
        if response.status_code != 200:
            print(f"[錯誤] 無法訪問: {normalized_url} (HTTP {response.status_code})")
            return
        
        # 檢查關鍵字
        page_content = response.text
        for keyword in keywords:
            if keyword in page_content:
                found_keywords.append((normalized_url, keyword))
                print(f"[發現] 在 {normalized_url} 找到關鍵字: {keyword}")

        # 解析網頁
        soup = BeautifulSoup(page_content, "html.parser")
        links = soup.find_all("a", href=True)
        for link in links:
            full_url = urljoin(normalized_url, link['href'])
            if base_url in full_url:  # 僅處理主域名的子頁面
                crawl(full_url)
    except Exception as e:
        print(f"[錯誤] 無法處理 {url}，原因: {e}")

# 開始爬取
print("[開始] 爬取網站及子網址關鍵字搜尋")
crawl(base_url)

# 總結
print(f"[完成] 爬蟲結束，共檢查了 {checked_count} 個網址")
if found_keywords:
    print("[結果] 以下頁面包含關鍵字:")
    for url, keyword in found_keywords:
        print(f"- {url} (關鍵字: {keyword})")
else:
    print("[結果] 未找到任何關鍵字")