import xlsxwriter
import socket
import requests
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 定義要檢測的端口列表
ports = [80, 443, 8080, 8443, 5000, 5001, 5002, 5003, 5004, 5005]

# IP 列表文件和輸出文件的位置
ip_file_path = "/home/kali/Sys/CheckWebServices/ScanNetworkVlan/ScanNetwork_Vlan-v1.txt"  # CIDR 或 IP 地址的清單
output_file_path = "/home/kali/Sys/CheckWebServices/ScanNetworkVlan/ScanNetwork_Vlan-final-result.xlsx"

# 創建工作簿和工作表
workbook = xlsxwriter.Workbook(output_file_path)
worksheet = workbook.add_worksheet()

# 設置標題行
worksheet.write(0, 0, "IP地址")
worksheet.write(0, 1, "可用端口")
worksheet.write(0, 2, "HTTP/HTTPS 響應")

timeout = 2  # 設置 TCP 連接和 HTTP 請求的超時（2秒）

def check_ip(ip):
    available_ports = []
    http_responses = []

    # 檢查每個端口
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))

            if result == 0:
                available_ports.append(str(port))

                if port == 80:
                    url = f"http://{ip}:{port}"
                elif port == 443 or port == 8443:
                    url = f"https://{ip}:{port}"
                else:
                    url = f"http://{ip}:{port}"

                try:
                    response = requests.get(url, timeout=timeout)
                    if response.status_code == 200:
                        http_responses.append(f"{url} (Status: {response.status_code})")
                    else:
                        http_responses.append(f"{url} (Status: {response.status_code}, Error)")
                except requests.exceptions.Timeout:
                    http_responses.append(f"{url} (Timeout)")
                except requests.exceptions.RequestException as e:
                    http_responses.append(f"{url} (Failed: {str(e)})")
            else:
                http_responses.append(f"Port {port} on {ip} is closed.")

        except socket.timeout:
            http_responses.append(f"Timeout connecting to {ip}:{port}")
        except Exception as e:
            http_responses.append(f"Error checking {ip}:{port} - {str(e)}")

    return ip, available_ports, http_responses

# 實時寫入到 Excel 檔案
def write_result(row, ip, available_ports, http_responses):
    worksheet.write(row, 0, ip)
    if available_ports:
        worksheet.write(row, 1, ", ".join(available_ports))
        worksheet.write(row, 2, "\n".join(http_responses))
    else:
        worksheet.write(row, 1, "無可用端口")
        worksheet.write(row, 2, "無 HTTP/HTTPS 響應")

# 多線程執行並顯示進度
all_ips = []
with open(ip_file_path, "r") as ip_file:
    for line in ip_file:
        line = line.strip()
        if line:  # 忽略空行
            try:
                network = ipaddress.ip_network(line, strict=False)
                all_ips.extend([str(ip) for ip in network.hosts()])
            except ValueError:
                print(f"無效的 IP 或網段格式：{line}")

# 使用進度條顯示進度
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(check_ip, ip): ip for ip in all_ips}
    row = 1
    for future in tqdm(as_completed(futures), total=len(futures), desc="掃描進度"):
        ip, available_ports, http_responses = future.result()
        write_result(row, ip, available_ports, http_responses)
        row += 1

# 關閉工作簿，並添加錯誤處理
try:
    workbook.close()
except Exception as e:
    print(f"關閉工作簿時出錯: {str(e)}")

print(f"檢測完成，結果已即時寫入 {output_file_path}")