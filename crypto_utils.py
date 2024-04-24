import os
import requests

# crypto_utils.py


def get_account_balance(address, api_key):
    """Retrieve the account balance from the ScrollScan API."""
    url = 'https://api.scrollscan.com/api'
    params = {
        'module': 'account',
        'action': 'balance',
        'address': address,
        'tag': 'latest',
        'apikey': api_key
    }
    response = requests.get(url, params=params)
    return response.json() if response.ok else (response.status_code, response.reason)


def wei_to_eth(wei_balance):
    """Convert wei value to ETH."""
    return int(wei_balance) / 1e18


def get_eth_price():
    """Retrieve the current price of ETH in USD."""
    url = "https://min-api.cryptocompare.com/data/price"
    params = {
        'fsym': 'ETH',
        'tsyms': 'USD'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return None


def get_eth_balance_in_usd(address, api_key):
    """Get the balance of an address in ETH and convert it to USD."""
    balance_info = get_account_balance(address, api_key)
    if 'result' in balance_info and balance_info['result'] is not None:
        wei_balance = balance_info['result']
        ether_balance = wei_to_eth(wei_balance)

        eth_price_info = get_eth_price()
        if eth_price_info and 'USD' in eth_price_info:
            usd_balance = ether_balance * eth_price_info['USD']
            return ether_balance, usd_balance
    return None, None
