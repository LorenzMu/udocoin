import requests
import os,pathlib
import json

def seed_is_active(ip:str)->bool:
    try:
        response = requests.get(f"{ip}/get/is_active")
        return response.status_code == 200
    except:
        return False

def get_known_seeds():
    seeds = json.load(open(os.path.join(pathlib.Path(__file__).parent,"seeds.json")))
    active_seeds = []
    for seed in seeds:
        if seed_is_active(seed):
            active_seeds.append(seed)
    print("Found as active seeds: ",active_seeds)
    return active_seeds

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
            response = requests.get(f"{seed}/miner/get_balance/{public_key}")
            if response.status_code == 200:
                return str(response.text)
        except:
            pass
    return "N/a"