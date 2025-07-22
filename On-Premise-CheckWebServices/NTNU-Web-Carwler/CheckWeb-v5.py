import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

# 主網址與關鍵字
base_url = "https://www.ntnu.edu.tw/president/"
keywords = ["吳正己"]

# 已訪問的網址集合
visited_urls = set()

# 紀錄進度
checked_count = 0
found_keywords = []

# 使用 Selenium 抓取動態內容
def fetch_dynamic_content(url):
    try:
        service = Service("D:\NTNU-DevOps\chrome-win64\chrome.exe")  # 替換為 ChromeDriver 路徑
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # 無頭模式
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_content = driver.page_source
        return page_content
    except Exception as e:
        print(f"[錯誤] Selenium 無法抓取 {url}，原因: {e}")
        return None
    finally:
        driver.quit()

# 爬取頁面內容
def crawl(url):
    global checked_count
    try:
        # 正規化 URL
        normalized_url = re.sub(r"#.*", "", url)
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

        # 使用 Selenium 抓取動態內容
        page_content = response.text
        dynamic_content = fetch_dynamic_content(normalized_url)
        if dynamic_content:
            page_content = dynamic_content

        # 檢查關鍵字
        for keyword in keywords:
            if keyword.lower() in page_content.lower():
                found_keywords.append((normalized_url, keyword))
                print(f"[發現] 在 {normalized_url} 找到關鍵字: {keyword}")

        # 解析網頁中的連結
        soup = BeautifulSoup(page_content, "html.parser")
        links = soup.find_all("a", href=True)
        for link in links:
            full_url = urljoin(normalized_url, link["href"])
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