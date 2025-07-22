import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# 設置 Selenium 驅動的配置
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 無頭模式，不顯示瀏覽器窗口
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# 爬取網站並提取子頁面連結
def get_all_links(driver, base_url):
    driver.get(base_url)
    time.sleep(5)  # 等待網頁加載
    links = driver.find_elements(By.TAG_NAME, 'a')
    all_links = set()
    for link in links:
        url = link.get_attribute('href')
        if url and base_url in url:  # 濾掉外部連結
            all_links.add(url)
    return all_links

# 爬取並檢查網頁中的關鍵字
def check_for_keywords(url, keywords):
    print(f"[進度] 正在檢查: {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            for keyword in keywords:
                if keyword in page_text:
                    print(f"[找到] 關鍵字: {keyword} 在 {url}")
                    return True
        return False
    except requests.exceptions.RequestException as e:
        print(f"[錯誤] 請求錯誤: {e}")
        return False

# 主程式
def main():
    base_url = "https://www.ntnu.edu.tw/president/"
    keywords = ["吳正己"]  # 搜索的關鍵字
    visited_urls = set()

    # 初始化 Selenium 驅動
    driver = create_driver()

    # 爬取網站和子目錄
    print("[開始] 爬取網站及子網址關鍵字搜尋")
    links_to_check = get_all_links(driver, base_url)
    visited_urls.add(base_url)

    for link in links_to_check:
        if link not in visited_urls:
            visited_urls.add(link)
            if not check_for_keywords(link, keywords):
                # 若未找到關鍵字，再爬取子目錄中的頁面
                sub_links = get_all_links(driver, link)
                for sub_link in sub_links:
                    if sub_link not in visited_urls:
                        visited_urls.add(sub_link)
                        check_for_keywords(sub_link, keywords)

    driver.quit()  # 關閉 Selenium 驅動
    print("[完成] 爬蟲結束，共檢查了", len(visited_urls), "個網址")

if __name__ == "__main__":
    main()