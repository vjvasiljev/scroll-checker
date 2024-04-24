import requests
from datetime import datetime


def get_transaction_list(address, startblock, endblock, page, offset, sort, api_key):
    """Retrieve a list of transactions for the given address."""
    url = 'https://api.scrollscan.com/api'
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': startblock,
        'endblock': endblock,
        'page': page,
        'offset': offset,
        'sort': sort,
        'apikey': api_key
    }

    response = requests.get(url, params=params)
    return response.json() if response.ok else (response.status_code, response.reason)


def get_unique_periods(transactions):
    """Get unique days, weeks and months from the list of transactions."""
    unique_days = set()
    unique_weeks = set()
    unique_months = set()
    for tx in transactions:
        if tx.get('txreceipt_status') == '1':
            tx_date = datetime.utcfromtimestamp(int(tx['timeStamp'])).date()
            unique_days.add(tx_date)  # Store unique days
            unique_weeks.add(tx_date.isocalendar()[:2])  # Store unique weeks
            unique_months.add((tx_date.year, tx_date.month)
                              )  # Store unique months
    return len(unique_days), len(unique_weeks), len(unique_months)


def count_transactions_and_analyze(transaction_list, eth_rate):
    """Analyze transaction data to gather various metrics."""
    transactions = transaction_list.get('result', [])
    num_total_transactions = len(transactions)
    num_successful_transactions = sum(
        tx.get('txreceipt_status') == '1' for tx in transactions)

    unique_days, unique_weeks, unique_months = get_unique_periods(transactions)

    # Count unique contracts interacted with
    unique_contracts = {tx['to']
                        for tx in transactions if tx.get('input') != '0x'}

    num_unique_contracts = len(unique_contracts)

    # Compute the total volume and gas fees in both ETH and USD
    total_volume_wei = sum(
        int(tx['value']) for tx in transactions if tx.get('txreceipt_status') == '1')
    total_gas_fees_wei = sum(int(tx['gasUsed']) * int(tx['gasPrice'])
                             for tx in transactions if tx.get('txreceipt_status') == '1')

    # Convert wei to ETH
    total_volume_eth = total_volume_wei / 1e18
    total_gas_fees_eth = total_gas_fees_wei / 1e18

    # Convert ETH to USD
    total_volume_usd = total_volume_eth * eth_rate
    total_gas_fees_usd = total_gas_fees_eth * eth_rate

    # Return all the computed metrics
    return (
        num_total_transactions,
        num_successful_transactions,
        num_unique_contracts,
        unique_days,
        unique_weeks,
        unique_months,
        total_volume_eth,
        total_gas_fees_eth,
        total_volume_usd,
        total_gas_fees_usd
    )
