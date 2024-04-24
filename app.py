from flask import Flask, request, render_template
from crypto_utils import get_eth_balance_in_usd
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        address = request.form['address']
        api_key = os.getenv('SCROLLSCAN_API_KEY')

        eth_balance, usd_balance = get_eth_balance_in_usd(address, api_key)
        if eth_balance is not None and usd_balance is not None:
            return render_template('results.html', address=address, eth_balance=eth_balance, usd_balance=usd_balance)
        else:
            error_message = "Unable to retrieve balance information."
            return render_template('index.html', error=error_message)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
