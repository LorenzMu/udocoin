
import requests
# check if miner is running on port 80 or 5000
address = "http://localhost"
try:
    port_80_is_active = requests.get("http://localhost/get/is_active").status_code == 200
except:
    port_80_is_active = False

if not port_80_is_active:
    address = "http://localhost:5000"

print(f"Testing consensus on {address}")

print(requests.get(f"{address}/consensus_test",timeout=10).text)