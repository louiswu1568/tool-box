import requests
from requests.exceptions import RequestException
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# 目標網址
urls = [
    "https://www.ntnu.edu.tw/static.php?id=colleges",
    "https://www.ntnu.edu.tw/static.php?id=adm",
    "https://www.ntnu.edu.tw/static.php?id=faculty"
]

output_file = "output.txt"

# 儲存所有唯一的網址
unique_urls = set()

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

            for link in links:
                link_url = link['href']
                
                # 使用 urljoin 處理相對路徑
                link_url = urljoin(target_url, link_url)

                # 提取網址的主機名稱（netloc）並去掉後面的路徑部分
                parsed_url = urlparse(link_url)
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

                # 加入唯一網址集合中
                unique_urls.add(clean_url)

        except RequestException:
            continue  # 忽略錯誤並繼續處理下一個網址

    # 寫入唯一的網址到文件，只保留主機名稱部分
    for url in unique_urls:
        file.write(f"{url}\n")

print(f"URL 檢查完成，結果已保存至 {output_file}")