import ssl
import socket
import pandas as pd
from datetime import datetime

def get_ssl_certificate_expiry(hostname, port=443):
    """取得網站的 SSL 憑證起始與到期日期"""
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        # 解析憑證日期
        not_before = datetime.strptime(cert['notBefore'], "%b %d %H:%M:%S %Y %Z")
        not_after = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")

        return not_before, not_after
    except Exception as e:
        return None, None

# 指定檔案路徑
# 記得創建一個 website.txt 去存要檢查的網站
file_path = "website.txt"

# 讀取檔案並移除 "https://" 或 "http://"
with open(file_path, "r") as f:
    websites = [line.strip().replace("https://", "").replace("http://", "") for line in f.readlines() if line.strip()]

# 建立結果表格
results = []
for site in websites:
    start_date, expiry_date = get_ssl_certificate_expiry(site)
    results.append([site, start_date, expiry_date])

# 轉換為 DataFrame 並顯示
df = pd.DataFrame(results, columns=["網站", "憑證生效日期", "憑證到期日期"])
print(df.to_string())  # 直接輸出 DataFrame

# 儲存為 CSV 檔案
output_csv = "ssl_certificates.csv"
df.to_csv(output_csv, index=False)
print(f"結果已儲存至 {output_csv}")
