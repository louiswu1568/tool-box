from gvm.connections import TLSConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform

# OpenVAS connection details
host = "127.0.0.1"
port = 9392
username = "louiswu"
password = "your_password"  # Replace with actual password

# Prompt for user input
cve_id = input("請輸入 CVE 編號（例如：CVE-2023-XXXXX）：")
cpe = input("請輸入 CPE 編號（例如：cpe:/a:vendor:product:version）：")

# Establish TLS connection to OpenVAS
connection = TLSConnection(hostname=host, port=port)
transform = EtreeTransform()

# Connect and authenticate
with Gmp(connection, transform=transform) as gmp:
    gmp.authenticate(username, password)
    
    # Retrieve CVE information
    cve_info = gmp.get_cves(cve_id=cve_id)
    print(f"CVE 資訊：\n{cve_info}")

    # Retrieve CPE information
    cpe_info = gmp.get_cpes(cpe=cpe)
    print(f"CPE 資訊：\n{cpe_info}")
