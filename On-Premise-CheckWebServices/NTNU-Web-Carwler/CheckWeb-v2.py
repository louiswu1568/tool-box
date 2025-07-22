import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 基本設定
base_url = "https://cve.ntnu.edu.tw/"
keywords = ["蔡富貴詐騙", "廖肇衍", "臺師大"]
visited_urls = set()  # 紀錄已訪問的網址
keyword_found = False  # 紀錄是否找到關鍵字

# 爬取函數
def crawl(url, total_urls, current_count):
    global keyword_found

    if url in visited_urls:  # 避免重複訪問
        return current_count
    visited_urls.add(url)
    current_count += 1

    print(f"[進度] 檢查中 ({current_count}/{total_urls}): {url}")
    
    try:
        # 發送 HTTP GET 請求
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 確保請求成功
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 搜索關鍵字
        for keyword in keywords:
            if keyword in response.text:
                print(f"[找到] 關鍵字 '{keyword}' 在 {url}")
                keyword_found = True
        
        # 搜尋所有<a>標籤中的子網址
        for link in soup.find_all("a", href=True):
            href = link["href"]
            # 處理相對路徑，組成完整的 URL
            full_url = urljoin(base_url, href)
            # 限制只爬取同一域名的網址
            if base_url in full_url and full_url not in visited_urls:
                total_urls = crawl(full_url, total_urls, current_count)
    except Exception as e:
        print(f"[錯誤] 無法訪問 {url}: {e}")
    
    return current_count

# 預先估算總子網址數量
def estimate_total_urls(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        return len(links)
    except Exception as e:
        print(f"[錯誤] 無法訪問 {url}: {e}")
        return 0

# 主執行流程
print("[開始] 爬取網站及子網址關鍵字搜尋")
total_urls = estimate_total_urls(base_url) + 1  # 主網址 + 子網址數
if total_urls == 1:
    print("[錯誤] 無法估算子網址數量，可能無法進行爬蟲")
else:
    print(f"[預估] 總共需要檢查 {total_urls} 個網址")
    final_count = crawl(base_url, total_urls, 0)
    if not keyword_found:
        print("[結果] 未找到任何關鍵字")
    print(f"[完成] 爬蟲結束，共檢查了 {final_count} 個網址")