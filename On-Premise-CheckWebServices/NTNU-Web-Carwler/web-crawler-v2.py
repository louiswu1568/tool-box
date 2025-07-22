import requests
from requests.exceptions import RequestException
import socket
from bs4 import BeautifulSoup

# 目標網址
urls = [
    "https://www.ntnu.edu.tw/static.php?id=colleges",
    "https://www.ntnu.edu.tw/static.php?id=adm",
    "https://www.ntnu.edu.tw/static.php?id=faculty"
]

output_file = "output.txt"

# 開啟輸出檔案
with open(output_file, "w", encoding="utf-8") as file:
    for target_url in urls:
        try:
            # 發送請求並獲取網頁內容
            response = requests.get(target_url)
            response.raise_for_status()  # 檢查是否返回 4xx 或 5xx 錯誤

            # 解析 HTML 原始碼
            soup = BeautifulSoup(response.text, 'html.parser')

            # 找出所有學院系所的連結（假設連結在 <a> 標籤中）
            links = soup.find_all('a', href=True)

            for i, link in enumerate(links, 1):
                link_url = link['href']
                if not link_url.startswith("http"):
                    link_url = "https://www.ntnu.edu.tw" + link_url  # 處理相對路徑

                try:
                    # 請求每個學院系所的 URL
                    sub_response = requests.get(link_url, timeout=10)
                    sub_response.raise_for_status()  # 檢查是否返回 4xx 或 5xx 錯誤
                    file.write(f"URL {i}: {link_url} - 成功\n")
                except socket.gaierror:  # 網域解析錯誤
                    file.write(f"URL {i}: {link_url} - 錯誤 (無法解析域名)\n")
                except RequestException as e:
                    file.write(f"URL {i}: {link_url} - 錯誤 (請求異常: {str(e)})\n")

        except RequestException as e:
            file.write(f"無法獲取網頁內容 {target_url}: {str(e)}\n")

print(f"URL 檢查完成，結果已保存至 {output_file}")
