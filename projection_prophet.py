import logging
import numpy as np
import pandas as pd

from datetime import timedelta, date
from fbprophet import Prophet
from historical_prices import load_prices
from json import dumps

days_ago_presets = [20 * (i + 1) for i in range(5)]    # last 5 months, 20 by 20 work week days


def convert_string_date(date_str):
    return date(*[int(d) for d in date_str.split('-')])


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def find_weekend_days(start_date_str, end_date_str):
    start_date = convert_string_date(start_date_str)
    end_date = convert_string_date(end_date_str)

    return [d.strftime("%Y-%m-%d") for d in daterange(start_date, end_date) if d.weekday() >= 5]


def find_ticker_index(ticker_prices, date_str):
    for i in range(len(ticker_prices) - 1, 0, -1):
        if ticker_prices[i][0] == date_str:
            return i

    return -1


def compute_mse(dicts):
    ys = [d['y'] for d in dicts if 'y' in d.keys()]
    yhats = [d['yhat'] for d in dicts if 'y' in d.keys()]

    return np.square(np.subtract(ys, yhats)).mean()


def predict_future(ticker_prices, days_to_predict):
    weekend_days = find_weekend_days(ticker_prices[0][0], ticker_prices[-1][0])
    weekends_in_range = pd.DataFrame({
        'holiday': 'weekend',
        'ds': pd.to_datetime(weekend_days),
        'lower_window': 0,
        'upper_window': 0,
    })

    df = pd.DataFrame.from_records(ticker_prices, columns=['ds', 'y'])
    m = Prophet(holidays=weekends_in_range)
    m.fit(df)
    future = m.make_future_dataframe(periods=days_to_predict)
    return m.predict(future)


def build_response(forecast, ticker_prices, days):
    forecast_tail = forecast.tail(days)[['ds', 'yhat']]
    forecast_tail = forecast_tail[forecast_tail['ds'].dt.dayofweek < 5]     # filter only work week days
    dicts = forecast_tail.to_dict('records')
    dicts = [{
        'ds': d['ds'].strftime('%Y-%m-%d'),
        'yhat': round(d['yhat'], 2)
    } for d in dicts]

    index = find_ticker_index(ticker_prices, dicts[0]['ds'])
    for i in range(index, len(ticker_prices)):
        dicts[i - index]['y'] = ticker_prices[i][1]

    return dicts


def compute_best_projection(ticker_prices, days_to_predict):
    best_mse = float('inf')
    best_dicts = None
    best_days_ago = None

    for days_ago in days_ago_presets:
        if days_ago > len(ticker_prices):
            break

        days = int(days_ago * 0.2) + days_to_predict     # last 20% of work week days + predicted days
        sliced_ticker_prices = ticker_prices[-days_ago:]
        forecast = predict_future(sliced_ticker_prices, days_to_predict)
        dicts = build_response(forecast, sliced_ticker_prices, days)
        mse = compute_mse(dicts)

        logging.info('Work week days ago: %d' % days_ago)
        logging.info('20%s work week days ago: %d' % ('%', int(days_ago * 0.2)))
        logging.info('Predicted days: %d' % days_to_predict)
        logging.info('MSE: %.2f%s' % (mse * 100, '%'))

        if mse < best_mse:
            best_dicts = dicts
            best_mse = mse
            best_days_ago = days_ago

    logging.info('Best fit result found using %d week days ago with MSE %.2f%s' % (best_days_ago, best_mse * 100, '%'))

    return best_days_ago, best_mse, best_dicts


def project(ticker):
    ticker_prices = load_prices(ticker, parse_json=False)
    days_to_predict = 6
    days_ago, mse, dicts = compute_best_projection(ticker_prices, days_to_predict)

    return dumps({
        'daysAgo': days_ago,
        'meanSquaredError': mse,
        'items': dicts
    })
