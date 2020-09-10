from datetime import datetime
from flask import Flask, jsonify
from financial_indicators import load_indicators
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


@app.route('/indicators', methods=['GET'])
def indicators():
    global indicators_list, day

    if day != datetime.strftime(datetime.today(), '%d'):
        indicators_list, day = reload_indicators()

    return jsonify(indicators_list)


if __name__ == '__main__':
    port = int(environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
