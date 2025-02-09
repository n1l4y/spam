import pandas as pd
import threading
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
import hashlib
import time
from math import floor
import json
from apscheduler.schedulers.blocking import BlockingScheduler
load_dotenv("./.env")
U_ID = os.getenv("U_ID")

def md5_hash(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()

def get_contract_size(symbol):
    return requests.get('https://contract.mexc.com/api/v1/contract/detail', params={'symbol': symbol}).json()['data']['contractSize']

def gen_header():
    global U_ID
    return {
    'authorization': U_ID,
    'content-type': 'application/json',
    # cookie
    'origin': 'https://futures.mexc.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
}

def get_mxc_sign(data):
    global U_ID
    _ = int(time.time() * 1000)
    o = md5_hash(U_ID + str(_))[7:]
    sign = md5_hash(str(_) + data + o)
    return str(_), sign


def spot_place_order(coin_id, price, quantity):
    global U_ID
    url = 'https://mexc.com/api/platform/spot/order/place?mh=34bfecbfd72ad383726040d65f159f45'
    
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'language': 'en-US',
        'origin': 'https://www.mexc.com',
        'pragma': 'akamai-x-cache-on',
        'priority': 'u=1, i',
        'referer': 'https://www.mexc.com/exchange/',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        # cookie
        'content-type': 'application/json',
        'authorization': U_ID,
    }   
   
    data = {
        'currencyId': coin_id, 
        'marketCurrencyId': '128f589271cb4951b03e71e6323eb7be', 
        'tradeType': 'BUY', 
        'price': str(price), 
        'quantity': str(quantity), 
        'orderType': 'LIMIT_ORDER', 
       


       
        'ts': int(time.time() * 1000), 
        'mhash': '34bfecbfd72ad383726040d65f159f45'}
    
    str_data = json.dumps(data, separators=(',', ':'))
    headers['x-mxc-nonce'], headers['x-mxc-sign'] = get_mxc_sign(str_data)
    
    response = requests.post(url, headers=headers, data=str_data)
    response.raise_for_status()
    res = response.json()
    res
    if not res['msg'] == 'success':
        raise Exception('Failed to place order:', res['msg'])
    else:
        print('PLACED ORDER:', res['data']['orderId'])
        return True

spot_place_order('e47c124c41d549449b2dfbb36c8c5fb8', 5, 2)
