import requests
import time

# 讀取學術單位清單
def read_academic_units(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 假設每行是不同的學術單位名稱
            academic_units = file.readlines()
            academic_units = [unit.strip() for unit in academic_units if unit.strip()]
            return academic_units
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {file_path}")
        return []
    except Exception as e:
        print(f"錯誤：讀取檔案時發生錯誤 ({str(e)})")
        return []

# 模擬 URL 拼接並輸出，這裡假設每個單位的 URL 根據名稱生成
def generate_urls(unit_list):
    urls = []
    base_url = "http://example.ntnu.edu.tw/"  # 假設每個學院的 URL 是這個基礎 URL
    for unit in unit_list:
        # 使用單位名稱生成 URL，並移除空格、轉為小寫
        url = f"{base_url}{unit.replace(' ', '').lower()}"
        urls.append(url)
    return urls

# 優化 URL 輸出處理並將結果寫入文字檔
def output_urls_to_file(academic_units):
    if not academic_units:
        print("沒有學術單位資料可處理")
        return
    
    urls = generate_urls(academic_units)
    
    # 開啟檔案以寫入模式，如果檔案不存在會自動建立
    with open("output_urls.txt", "w", encoding="utf-8") as file:
        for i, url in enumerate(urls):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    file.write(f"URL {i+1}: {url} - 成功\n")
                else:
                    file.write(f"URL {i+1}: {url} - 錯誤 (狀態碼 {response.status_code})\n")
            except requests.exceptions.RequestException as e:
                file.write(f"URL {i+1}: {url} - 錯誤 ({str(e)})\n")
            
            # 可選：為防止被封鎖，增加延遲
            time.sleep(0.5)

# 讀取檔案，並將學術單位清單傳遞給 output_urls_to_file
academic_units = read_academic_units("academic_units/unit-v1.txt")

# 開始執行並將結果寫入檔案
output_urls_to_file(academic_units)
