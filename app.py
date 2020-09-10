from datetime import datetime
from flask import Flask, jsonify, request
from financial_indicators import load_indicators
from historical_prices import load_prices
from os import environ


def reload_indicators():
    indicators_data, today = dict(load_indicators()), datetime.strftime(datetime.today(), '%d')
    indicators_data = {
        outer_k: {
            inner_k: float(inner_v) for inner_k, inner_v in outer_v.items()
        } for outer_k, outer_v in indicators_data.items()
    }

    return indicators_data, today


app = Flask(__name__)
indicators_list, day = reload_indicators()


@app.route('/', methods=['GET'])
def root():
    return 'Stock Projection Service is running'


@app.errorhandler(404)
def page_not_found(e):
    return 'Not Found (404)', 404


@app.route('/indicators', methods=['GET'])
def indicators():
    global indicators_list, day

    if day != datetime.strftime(datetime.today(), '%d'):
        indicators_list, day = reload_indicators()

    return jsonify(indicators_list)


@app.route('/prices', methods=['GET'])
def prices():
    query_parameters = request.args
    ticker = query_parameters.get('ticker')

    return load_prices(ticker) if ticker else page_not_found(404)


if __name__ == '__main__':
    port = int(environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
