import requests
from requests.exceptions import RequestException
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import socket
from collections import defaultdict

# 目標網址
urls = [
    "https://www.ntnu.edu.tw/static.php?id=colleges",
    "https://www.ntnu.edu.tw/static.php?id=adm",
    "https://www.ntnu.edu.tw/static.php?id=faculty"
]

output_file = "output.txt"

# 儲存所有唯一的網址
unique_urls = set()
ip_to_domains = defaultdict(set)  # 用 set 避免重複網址

# 開啟輸出檔案
with open(output_file, "w", encoding="utf-8") as file:
    for target_url in urls:
        try:
            # 發送請求並獲取網頁內容
            response = requests.get(target_url, timeout=5)
            response.raise_for_status()  # 檢查是否返回 4xx 或 5xx 錯誤

            # 解析 HTML 原始碼
            soup = BeautifulSoup(response.text, 'html.parser')

            # 找出所有 <a> 標籤的連結
            links = soup.find_all('a', href=True)

            for link in links:
                link_url = link['href']
                
                # 使用 urljoin 處理相對路徑
                link_url = urljoin(target_url, link_url)

                # 只保留來自 ntnu.edu.tw 的網址
                if "ntnu.edu.tw" in link_url:
                    unique_urls.add(link_url)

        except RequestException:
            continue  # 忽略錯誤並繼續處理下一個網址

    # 解析 Domain 並分組儲存
    for url in unique_urls:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc  # 取得 domain，例如 www.ntnu.edu.tw
        
        try:
            # 使用 socket.gethostbyname() 解析 IP
            ip_address = socket.gethostbyname(domain)
            ip_to_domains[ip_address].add(url)  # 依照 IP 分組（使用 set 避免網址重複）
        except socket.gaierror:
            ip_to_domains["解析失敗"].add(url)  # 如果解析失敗，放入 "解析失敗" 類別

    # 依 IP 分類輸出（確保每個 IP 只出現一次）
    for ip, domains in ip_to_domains.items():
        for domain in sorted(domains):  # 讓網址排序，輸出更整齊
            file.write(f"#{domain}\n")
        file.write(f"{ip}\n\n")  # IP 地址換行，分組顯示

print(f"URL 檢查完成，結果已保存至 {output_file}")