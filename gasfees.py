def calculate_total_transaction_fee(transaction):
    # Extract necessary data from the transaction
    gas_used = int(transaction['gasUsed'])
    gas_price = int(transaction['gasPrice'])

    # Calculate the total transaction fee in wei
    total_tx_fee_wei = gas_used * gas_price

    # Convert the total transaction fee to ETH (1 ETH = 10^18 wei)
    total_tx_fee_eth = total_tx_fee_wei / 1e18

    # Return the total transaction fee in ETH
    return total_tx_fee_eth


# Example usage:
transaction_data = {
    'blockNumber': '422179',
    'blockHash': '0x5467bd5b882d55ae6287f9882a1168f22cc555cb618919a0ba2d4334e1093eee',
    'timeStamp': '1698694940',
    'hash': '0x06b558dac22863fcd9489bb2c7dcf936fbf694e22789016893220d05a2ed65d1',
    'nonce': '19744',
    'transactionIndex': '0',
    'from': '0x80c67432656d59144ceff962e8faf8926599bcf8',
    'to': '0x4f5197cd2badf78cd5c63d7a1e0d8e7f0ed7e906',
    'value': '10000000000000186',
    'gas': '21000',
    'gasPrice': '660000000',
    'input': '0x',
    'methodId': '0x',
    'functionName': '',
    'contractAddress': '',
    'cumulativeGasUsed': '21000',
    'txreceipt_status': '1',
    'gasUsed': '21000',
    'confirmations': '4667008',
    'isError': '0'
}

# Call the function with transaction_data as input
total_tx_fee = calculate_total_transaction_fee(transaction_data)
print(f"Total Transaction Fee: {total_tx_fee} ETH")
