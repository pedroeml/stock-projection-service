import logging

from gevent import monkey
monkey.patch_all()

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
from financial_indicators import load_indicators
from historical_prices import load_prices
from os import environ
from projection_prophet import project

INDICATORS_DICT = None
WINNERS_DICT = None


def download_indicators():
    global INDICATORS_DICT
    logging.info('Indicators: loading...')

    indicators_data = dict(load_indicators())
    INDICATORS_DICT = {
        outer_k: {
            inner_k: float(inner_v) for inner_k, inner_v in outer_v.items()
        } for outer_k, outer_v in indicators_data.items()
    }
    logging.info('Indicators: loaded!')


def is_winner(ticker_indicators):
    return ticker_indicators['Div.Brut/Pat.'] < 1 and ticker_indicators['ROE'] >= 0 and ticker_indicators['ROIC'] >= 0 \
           and ticker_indicators['DY'] > 0.06


def load_winners():
    global INDICATORS_DICT
    global WINNERS_DICT
    logging.info('Winners: loading...')

    WINNERS_DICT = {
        ticker: {
            'Div.Brut/Pat.': indicators['Div.Brut/Pat.'],
            'ROE': indicators['ROE'],
            'ROIC': indicators['ROIC'],
            'DY': indicators['DY']
        } for ticker, indicators in INDICATORS_DICT.items() if is_winner(indicators)
    }
    logging.info('Winners: loaded!')


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MONGO_URI'] = 'mongodb://' + environ['MONGODB_USERNAME'] + ':' + environ['MONGODB_PASSWORD'] + '@' + \
                          environ['MONGODB_HOSTNAME'] + ':27017/' + environ['MONGODB_DATABASE']
mongo = PyMongo(app)
db = mongo.db

download_indicators()
load_winners()


@app.route('/', methods=['GET'])
def index():
    return 'Stock Projection Service is running'


@app.errorhandler(404)
def page_not_found(e):
    return 'Not Found (404)', 404


@app.route('/indicators', methods=['GET'])
def indicators():
    global INDICATORS_DICT

    return jsonify(INDICATORS_DICT) if INDICATORS_DICT else page_not_found(404)


@app.route('/winners', methods=['GET'])
def winners():
    global WINNERS_DICT

    return jsonify(WINNERS_DICT) if WINNERS_DICT else page_not_found(404)


@app.route('/prices', methods=['GET'])
def prices():
    query_parameters = request.args
    ticker = query_parameters.get('ticker')

    return load_prices(ticker) if ticker else page_not_found(404)


@app.route('/projections', methods=['GET'])
def projections():
    query_parameters = request.args
    ticker = query_parameters.get('ticker')

    return project(ticker) if ticker else page_not_found(404)


if __name__ == '__main__':
    port = int(environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
