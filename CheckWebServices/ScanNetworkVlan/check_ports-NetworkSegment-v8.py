import xlsxwriter
import socket
import requests
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from datetime import datetime

# 定義要檢測的 Web 服務埠列表
ports = [
    80, 88, 102, 443, 502, 554, 1900, 2181, 2323, 2375, 2376, 3000, 3001,
    4200, 4443, 5000, 5001, 5006, 5007, 5600, 5601, 5700, 5984, 5985, 5986,
    6690, 6789, 7547, 8000, 8001, 8080, 8081, 8443, 8843, 8880, 8888, 9000,
    9200, 9300, 9443, 9999, 10000, 13131, 15672, 25565, 27017, 32400, 37777,
    44818, 49152, 49153, 49154, 49155, 49156, 49157, 49158, 49159, 49160,
    50070, 50075, 61000, 61001, 61002, 61003, 61004, 61005, 61006, 61007,
    61008, 61009, 65001
]

# IP 列表文件和輸出文件的位置
ip_file_path = "/home/kali/Sys/CheckWebServices/ScanNetworkVlan/ScanNetwork_Vlan-v1.txt"  # CIDR 或 IP 地址的清單

# 取得當前日期，格式為 yyyy-mm-dd
current_date = datetime.now().strftime("%Y-%m-%d")

# 修改 Excel 輸出路徑，將日期加入檔案名稱
output_file_path = f"/home/kali/Sys/OutputExcel/ScanNetwork_Vlan-final-result-{current_date}.xlsx"

# 創建工作簿和工作表
workbook = xlsxwriter.Workbook(output_file_path)
worksheet = workbook.add_worksheet()

# 設置標題行
worksheet.write(0, 0, "IP地址")
worksheet.write(0, 1, "可用Web TCP Port")
worksheet.write(0, 2, "HTTP/HTTPS Response")

timeout = 2  # 設置 TCP 連接和 HTTP 請求的超時（2秒）

def check_ip(ip):
    available_ports = []
    http_responses = []

    # 檢查每個Web TCP Port
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
        worksheet.write(row, 1, "無可用TCP Port")
        worksheet.write(row, 2, "無 HTTP/HTTPS Response")

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

#掃描內容涵蓋： By Louis Wu on 20250609
#(1)常見 Web & API 服務 Port（如 80、443、8080 等）
#(2)各大 NAS（Synology/QNAP 等）與 IoT 裝置常用 Port
#(3)工控設備/SCADA 通訊 Port
#(4)管理介面常見高位 Port
#(5)可疑或弱點常見 Port（如 2323、4443、10000 等）

#🔹 一、常見 Web 與 API Port
#Port#協定#用途說明
#80#HTTP#最常見 Web 預設 Port
#443#HTTPS#安全加密的 Web 通訊
#8080#HTTP-alt#常見測試或代理伺服器使用
#8443#HTTPS-alt#常見應用伺服器（如 Tomcat、Synology DSM）
#8000/8001#HTTP#Dev server（Node.js、Python Flask 等）
#8888#HTTP#Jupyter Notebook / Jenkins
#5000#HTTP#Flask / IoT 常用 port
#9443#HTTPS#Ubiquiti、Synology、Fortinet 等用於管理介面
#3000#HTTP#React、Grafana、Kibana 等 dev UI
#5601#HTTP#Elasticsearch Kibana dashboard

#🔹 二、常見 IoT / NAS / 家用設備 Web Port（含 API）
#✅ Synology NAS
#Port#說明
#5000#DSM Web 管理介面（HTTP）
#5001#DSM Web 管理介面（HTTPS）
#32400#Plex Media Server
#6690#Cloud Station
#5006#Synology Active Backup

#✅ QNAP NAS
#Port#說明
#8080#Web 管理介面（HTTP）
#443 / 8081#HTTPS 管理
#13131#Qsync Central
#32400#Plex
#9000#QTS Container Station

#✅ Ubiquiti (UniFi)
#Port#說明
#8443#UniFi 控制介面（HTTPS）
#8080#設備通信
#8880#HTTP Portal
#8843#HTTPS Portal
#6789#Speed Test
#443#設定 Portal

#✅ Hikvision / Dahua / IP Cam
#Port#說明
#80 / 88#Web 界面
#554#RTSP 串流
#5000~8000#裝置控制 API (如 ONVIF, ISAPI)
#37777#Dahua 特有服務
#65001#Dahua Cloud 傳輸 API

#✅ TP-Link / D-Link / ASUS / NETGEAR Router
#Port#說明
#80 / 443#Web UI（管理）
#8080#某些型號開放的遠端 UI
#2000 / 20005#ASUS AiCloud API
#7547#TR-069（遠端管理協定）👉 常見漏洞目標
#1900#SSDP / UPnP（IoT 設備掃描）

#🔹 三、工控 / SCADA / 監控管理用 Web Port
#Port#系統 / 用途#備註
#102#Siemens S7 通訊協定（S7comm）#有 Web 接口可能經由設備管理頁面
#44818#EtherNet/IP#常見於 Allen-Bradley 設備
#502#Modbus TCP#可 Web 前端顯示資料
#80/443#SCADA UI（Web HMI）#如 GE iFIX, Ignition
#8081#Web HMI（如 Inductive Automation）#
#5007#Schneider Electric（遠端監控）#

#🔹 四、冷門但常見於特定 Web API 的 Port
#Port#可能用途
#2375 / 2376#Docker API（HTTP / HTTPS）⚠️ 容易被誤開放
#5984#CouchDB（HTTP API）
#5985 / 5986#WinRM 管理接口（HTTP/HTTPS）
#9200 / 9300#Elasticsearch（HTTP / 叢集通訊）
#27017#MongoDB HTTP 服務（早期版本）
#50070 / 50075#Hadoop Web 介面
#15672#RabbitMQ HTTP 管理 API
#2181#Zookeeper Web API
#25565#Minecraft（某些自建 API 或服務介面也會用此）

#🔹 五、API 管理與監控平台常用 Port
#Port#平台 / 用途
#8001#Kong API Gateway 管理 API
#8000#Kong Proxy API
#9000#Portainer / Docker 管理平台
#9999#Spring Boot actuator、Netdata、Admin 控制介面
#3001#開發測試或副本站 Web UI
#4200#Angular 開發伺服器
#5600~5700#常見 DevOps 自訂 API 協定埠

#🔹 六、可疑或需注意的 Web Port（滲透測試重點）
#Port#說明
#4443#Fake SSL 管理（惡意軟體或自建 API）
#2323#Mirai IoT 殭屍網路常用備用 Telnet
#10000#Webmin / OpenVAS / Nessus（早期版本）
#49152~49160#Windows UPNP / IoT API 埠
#61000~65535#IoT / 雲台攝影機私有 Port，掃描要開大範圍

#✅ 建議用途
#滲透測試掃描（如：Nmap -p- / Masscan）
#制定防火牆白名單 / 黑名單
#IoT 資安防護測試
#建立資產盤點清單（特別是對 NAS 與中小企業設備）