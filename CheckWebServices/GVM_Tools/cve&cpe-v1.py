from gvm.connections import TLSConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform

# 設定 OpenVAS 伺服器的 URL 和連接埠
host = "140.122.67.55"
port = 9392

# 替換成您的帳號和密碼
username = "louiswu"
password = "j;3xj4yj320241107"

# 使用 TLS 連接至 OpenVAS
connection = TLSConnection(hostname=host, port=port)
transform = EtreeTransform()

# 連接至 GVM 並進行驗證
with Gmp(connection, transform=transform) as gmp:
    gmp.authenticate(username, password)
    
    # 查詢特定的 CVE 資訊（範例CVE編號）
    cve_id = "CVE-2023-XXXXX"
    cve_info = gmp.get_cves(cve_id=cve_id)
    print(f"CVE 資訊：\n{cve_info}")

    # 查詢特定的 CPE 資訊（範例CPE）
    cpe = "cpe:/a:vendor:product:version"
    cpe_info = gmp.get_cpes(cpe=cpe)
    print(f"CPE 資訊：\n{cpe_info}")
