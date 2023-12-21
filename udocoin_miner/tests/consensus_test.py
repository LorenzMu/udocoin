
import requests
# check if miner is running on port 80 or 5000
address = "http://localhost"
if not requests.get("http://localhost/get/is_active").status_code == 200:
    address = "http://localhost:5000"

print(requests.get(f"{address}/consensus",timeout=100).text)