import requests
import os,pathlib
import json

def seed_is_active(ip:str)->bool:
    try:
        response = requests.get(f"{ip}/get/is_active")
        # print(f"Response from {ip}",response)
        return response.status_code == 200
    except:
        return False

def get_known_seeds():
    username = "LorenzMu"
    repository = "udocoin"
    filename = "known_seeds.json"

    api_url = f"https://api.github.com/repos/{username}/{repository}/contents/{filename}"

    response = requests.get(api_url)

    if response.status_code == 200:
        content_info = response.json()
        content_base64 = content_info.get("content", "")
        import base64
        content = base64.b64decode(content_base64).decode('utf-8')
        seeds = json.loads(content)
        return seeds
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        raise Exception("Error getting seed list:", response.text)

def post_transaction(transaction:str)->str:
    transaction = json.load(transaction)
    active_seeds = get_known_seeds()
    for seed in active_seeds:
        response = requests.post(
            url=f"{seed}/miner/post_transaction",
            json=transaction)
        if response.status_code == 200 or response.status_code == 201:
            return response.text
    return None

def get_balance_by_public_key(public_key:str)->float:
    active_seeds = get_known_seeds()
    for seed in active_seeds:
        try:
            key = public_key.replace('\n','_')
            response = requests.get(f"{seed}/miner/get_balance?pubkey={key}")
            if response.status_code == 200:
                return str(response.text)
        except:
            pass
    return "N/a"

def send_transaction(signed_transaction:str):
    print("Sending transaction... ")
    active_seeds = get_known_seeds()
    transaction = json.loads(signed_transaction)
    print("transaction:", str(transaction))
    for seed in active_seeds:
        response = requests.post(f"{seed}/miner/post_transaction",json=transaction)
        print(str(response))
        print(str(response.status_code))
        print(str(response.text))
        if response.status_code == 200 or response.status_code == 201:
            return True
    return False