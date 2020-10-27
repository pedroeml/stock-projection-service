import pandas as pd

from datetime import timedelta, date
from fbprophet import Prophet
from historical_prices import load_prices
from json import dumps

days_ago_presets = [30*(i+1) for i in range(12)]
weekend_days = [5, 6]


def convert_string_date(date_str):
    return date(*[int(d) for d in date_str.split('-')])


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def find_weekend_days(start_date_str, end_date_str):
    start_date = convert_string_date(start_date_str)
    end_date = convert_string_date(end_date_str)

    return [d.strftime("%Y-%m-%d") for d in daterange(start_date, end_date) if d.weekday() in weekend_days]


def find_ticker_index(ticker_prices, date_str):
    for i in range(len(ticker_prices) - 1, 0, -1):
        if ticker_prices[i][0] == date_str:
            print('>> found index %d where %s' % (i, date_str))
            return i

    return -1


def project(ticker, days, days_ago):
    ticker_prices = load_prices(ticker, parse_json=False)
    ticker_prices = ticker_prices[-days_ago:]

    weekends_in_range = pd.DataFrame({
        'holiday': 'weekend',
        'ds': pd.to_datetime(find_weekend_days(ticker_prices[0][0], ticker_prices[-1][0])),
        'lower_window': 0,
        'upper_window': 1,
    })

    df = pd.DataFrame.from_records(ticker_prices, columns=['ds', 'y'])
    m = Prophet(holidays=weekends_in_range)
    m.fit(df)
    future = m.make_future_dataframe(periods=days)
    forecast = m.predict(future)
    dicts = forecast.tail(days*2).to_dict('records')
    dicts = [{
        'ds': d['ds'].strftime('%Y-%m-%d') if d['ds'] else None,
        'yhat': round(d['yhat'], 2)
    } for d in dicts if d['yhat'] > 0]

    index = find_ticker_index(ticker_prices, dicts[0]['ds'])
    for i in range(index, len(ticker_prices)):
        dicts[i - index]['y'] = ticker_prices[i][1]

    return dumps(dicts)
