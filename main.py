from collections import Counter
from datetime import datetime
import requests
from dotenv import load_dotenv
import os


def get_account_balance(address, api_key):
    url = 'https://api.scrollscan.com/api'
    params = {
        'module': 'account',
        'action': 'balance',
        'address': address,
        'tag': 'latest',
        'apikey': api_key
    }

    response = requests.get(url, params=params)

    if response.ok:
        return response.json()
    else:
        return response.status_code, response.reason


def wei_to_eth(wei_balance):
    # Convert string to an integer for arithmetic operations
    wei_balance = int(wei_balance)
    # 1 ether is 10^18 wei
    ether_value = wei_balance / 1e18
    return ether_value


def get_eth_price():
    # Construct the API endpoint URL
    url = "https://min-api.cryptocompare.com/data/price"
    parameters = {
        'fsym': 'ETH',
        'tsyms': 'BTC,USD,EUR'
    }

    # Make the GET request
    try:
        response = requests.get(url, params=parameters)
        # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        response.raise_for_status()
        data = response.json()

        # You can now access the price of ETH in BTC, USD and EUR like so:
        # eth_price_btc = data["BTC"]
        # eth_price_usd = data["USD"]
        # eth_price_eur = data["EUR"]

        return data
    except requests.RequestException as e:
        # Handle any errors that occur during the request
        print(f"An error occurred: {e}")
        return None


load_dotenv()  # This will load all the environment variables from a .env file.

api_key = os.getenv('SCROLLSCAN_API_KEY')

# Define a static value for the address, or leave it empty to prompt the user
# You can set this to a static value if needed
static_address = "0x4F5197CD2BAdF78Cd5C63d7a1E0D8E7F0eD7e906"

# Check if static_address is empty
if not static_address:
    # Prompt the user for input since static_address is empty
    address = input("Please enter the wallet address: ")
else:
    # Use the static value
    address = static_address

# Use address in the rest of your program
print(f"The wallet address is: {address}")

balance_info = get_account_balance(address, api_key)

# Extract the wei balance and convert to ether
wei_balance = balance_info['result']
ether_balance = wei_to_eth(wei_balance)

print(f'Balance: {ether_balance} ETH')


# Use the function to get the ETH price
eth_price = get_eth_price()

# Assuming both balance_info and eth_price are successful API responses,
# and eth_price contains 'USD' key:
if 'result' in balance_info and 'USD' in eth_price:
    usd_balance = ether_balance * eth_price['USD']
    print(f'Equivalent USD Balance: ${usd_balance:,.2f}')
else:
    print("There was an error retrieving the balance info or ETH price.")


def get_transaction_list(address, startblock, endblock, page, offset, sort, api_key):
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

    if response.ok:
        return response.json()
    else:
        return response.status_code, response.reason


# Optional: set these to static values, or add input prompts for these parameters
startblock = 0
endblock = 99999999
page = 1
offset = 1000
sort = 'asc'

# Example usage of get_transaction_list function
transaction_list = get_transaction_list(
    address, startblock, endblock, page, offset, sort, api_key)

# If the request was successful, we can print or process the transaction list
if isinstance(transaction_list, dict):
    for transaction in transaction_list.get('result', []):
        # print(transaction)  # or handle the transaction data as required
        x = 1
else:
    error_status_code, error_reason = transaction_list
    print(
        f"Error fetching transaction list: {error_status_code} {error_reason}")


def count_transactions_and_periods_with_unique_contracts_volume_and_fees(transaction_list):
    # Make sure we are accessing the list of transactions within the response
    transactions = transaction_list.get('result', [])

    # The number of total transactions
    num_total_transactions = len(transactions)

    # Accumulators for total volume and gas fees
    total_volume_wei = 0
    total_gas_fees_wei = 0

    # Initialize sets and list for tracking periods and contracts
    unique_weeks = set()
    unique_months = set()
    unique_contracts = set()
    unique_days_list = []

    # Iterate over transactions to process the required data
    for tx in transactions:
        # For successful transactions
        if tx.get('txreceipt_status') == '1':
            # Accumulate volume and gas fees
            total_volume_wei += int(tx['value'])
            total_gas_fees_wei += int(tx['gasUsed']) * int(tx['gasPrice'])

            # Calculate date information
            tx_date = datetime.utcfromtimestamp(int(tx['timeStamp'])).date()
            unique_days_list.append(tx_date)
            # Tuple of (year, week number)
            unique_weeks.add(tx_date.isocalendar()[0:2])
            # Tuple of (year, month number)
            unique_months.add((tx_date.year, tx_date.month))

            # Consider non-empty 'input' as contract interaction
            if tx.get('input') != '0x':
                unique_contracts.add(tx['to'])

    # Count unique days, weeks, and months
    date_counts = Counter(unique_days_list)
    num_unique_days = len(date_counts)
    num_unique_weeks = len(unique_weeks)
    num_unique_months = len(unique_months)

    # The number of successful transactions
    num_successful_transactions = len(
        [tx for tx in transactions if tx.get('txreceipt_status') == '1'])

    # The number of unique contracts interacted with
    num_unique_contracts = len(unique_contracts)

    # Convert total volume and gas fees from wei to ETH
    total_volume_eth = total_volume_wei / 1e18
    total_gas_fees_eth = total_gas_fees_wei / 1e18

    return (
        num_total_transactions,
        num_successful_transactions,
        num_unique_days,
        num_unique_weeks,
        num_unique_months,
        num_unique_contracts,
        total_volume_eth,
        total_gas_fees_eth,
    )


# Assuming 'transaction_list' is the variable holding the parsed JSON response from the API
(
    num_total_transactions,
    num_successful_transactions,
    num_unique_days,
    num_unique_weeks,
    num_unique_months,
    num_unique_contracts,
    total_volume_eth,
    total_gas_fees_eth
) = count_transactions_and_periods_with_unique_contracts_volume_and_fees(transaction_list)

# Output the results
print(f"Total number of transactions: {num_total_transactions}")
print(f"Number of successful transactions: {num_successful_transactions}")
print(f"Number of unique successful transaction days: {num_unique_days}")
print(f"Number of unique successful transaction weeks: {num_unique_weeks}")
print(f"Number of unique successful transaction months: {num_unique_months}")
print(f"Number of unique contracts interacted with: {num_unique_contracts}")
print(f"Total volume in ETH: {total_volume_eth}")
print(f"Total gas fees in ETH: {total_gas_fees_eth}")

eth_price = get_eth_price()
if eth_price and 'USD' in eth_price:
    eth_to_usd_rate = eth_price['USD']
else:
    print("Failed to retrieve the ETH price.")
    eth_to_usd_rate = None  # Set to None if the ETH price fetch failed

if eth_to_usd_rate is not None:
    total_volume_usd = total_volume_eth * eth_to_usd_rate
    total_gas_fees_usd = total_gas_fees_eth * eth_to_usd_rate

    print(f"Total volume in USD: ${total_volume_usd:,.2f}")
    print(f"Total gas fees in USD: ${total_gas_fees_usd:,.2f}")
else:
    print("ETH to USD rate not available. Cannot calculate the total volume and gas fees in USD.")
