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

INDICATORS_LIST = None


def reload_indicators():
    global INDICATORS_LIST
    logging.info('Indicators: loading...')

    indicators_data = dict(load_indicators())
    INDICATORS_LIST = {
        outer_k: {
            inner_k: float(inner_v) for inner_k, inner_v in outer_v.items()
        } for outer_k, outer_v in indicators_data.items()
    }
    logging.info('Indicators: loaded!')


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MONGO_URI'] = 'mongodb://' + environ['MONGODB_USERNAME'] + ':' + environ['MONGODB_PASSWORD'] + '@' + \
                          environ['MONGODB_HOSTNAME'] + ':27017/' + environ['MONGODB_DATABASE']
mongo = PyMongo(app)
db = mongo.db

reload_indicators()


@app.route('/', methods=['GET'])
def index():
    return 'Stock Projection Service is running'


@app.errorhandler(404)
def page_not_found(e):
    return 'Not Found (404)', 404


@app.route('/indicators', methods=['GET'])
def indicators():
    global INDICATORS_LIST

    return jsonify(INDICATORS_LIST) if INDICATORS_LIST else page_not_found(404)


@app.route('/prices', methods=['GET'])
def prices():
    query_parameters = request.args
    ticker = query_parameters.get('ticker')

    return load_prices(ticker) if ticker else page_not_found(404)


@app.route('/projections', methods=['GET'])
def projections():
    query_parameters = request.args
    ticker = query_parameters.get('ticker')
    days = query_parameters.get('days')
    days_ago = query_parameters.get('daysAgo')

    return project(ticker, int(days), int(days_ago)) if ticker and days else page_not_found(404)


if __name__ == '__main__':
    port = int(environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
