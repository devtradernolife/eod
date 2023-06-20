import json
import os
import re
import sys
import json
import time
import uuid
import shutil
import logging
import hashlib
import datetime
import itertools
import pandas as pd
from enum import Enum
from bs4 import BeautifulSoup
from datetime import timedelta
from dateutil.parser import parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3
from websocket import create_connection
import random
import string
from time import sleep
import requests

MAX_THREADS = 30
    
def requests_get(url, referer_url=None, headers=None, params=None, timeout=5, max_retries=5):
    session = requests.Session()
    headers = headers or {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'user-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
    }

    if referer_url:
        headers.update({'Referer': referer_url})

    for retry in range(max_retries):
        try:
            response = session.get(url, params=params, headers=headers, timeout=timeout)
            print('here: ',response)
            if response.status_code in (200, 404):
                print('yes')
                return response
        except Exception as e:
            pass
            print(e)
            # print(f'Request failed ({e}). Retrying ({retry}/{max_retries})...')
            # print(url)

    print(f'Failed to get response from {url} after {max_retries} retries.')
    return None

def get_security_info_from_settrade(symbol, language='en'):
        '''
        Fetches a stock info (only current listed stocks).
        '''
        url = f'https://www.settrade.com/api/set/stock/{symbol}/info'
        referer_url = f'https://www.settrade.com/th/equities/quote/{symbol}/overview'
        params = {
            'lang': language
        }

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'user-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
            'X-Channel': 'WEB_SETTRADE',
            'X-Client-Uuid': str(uuid.uuid4())
        }

        response = requests_get(url, referer_url, headers, params)
        return response, response.status_code

    
def get_current_listed_securities_from_settrade(security_type='S'):
    '''
    Fetches current listed securities from settrade website.

    Args:
        security_type list(str): S (Stock), L (ETF), X (DR), XF (DRx), V (DW), mai, TFEX, TBX.

    Returns:
        response: HTTP's response.
        status_code: HTTP's response.status_code.
    '''
    url = 'https://www.settrade.com/api/set/stock/list'
    referer_url = 'https://www.settrade.com/th/get-quote'
    params = {
        'securityType': security_type
    }
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'user-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
        'X-Channel': 'WEB_SETTRADE',
        'X-Client-Uuid': str(uuid.uuid4())
    }

    response = requests_get(url, referer_url, headers, params)
    print('here: ',response)
    return response, response.status_code
    
def get_current_listed_securities():
    output = []

    response, status = get_current_listed_securities_from_settrade(security_type='S')
    if status == 200:
        json_data = response.json()
        output = [symbol.get('symbol', '') for symbol in json_data.get('securitySymbols', [])]
    return output

def settrade_info_eod(symbols):

    ###### get date from intraval eod ######
    
    symbol = symbols[0]

    res = requests.get(f'https://www.settrade.com/api/set/stock/{symbol}/chart-quotation?period=1D&accumulated=false', 
    headers={'Referer': f'https://www.settrade.com/th/equities/quote/{symbol}/historical-trading'})

    if res.status_code != 200:
        print(f"Failed to get date for {symbol}")
        return 

    data = res.json()
    quotations = data.get('quotations', [])

    if not quotations:
        print(f"No quotations for {symbol}")
        return

    for symbol in symbols:
        symbol = symbol.upper()

        res_data, data_code = get_security_info_from_settrade('AEONTS')
        res_data = json.loads(res_data.text)

        print(res_data)

# call the function with list of symbols
# settrade_info_eod(['AEONTS'])


current_listed_securities = get_current_listed_securities()
settrade_info_eod(current_listed_securities)