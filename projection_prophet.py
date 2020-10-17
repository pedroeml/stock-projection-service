import pandas as pd

from fbprophet import Prophet
from historical_prices import load_prices
from json import dumps


def project(ticker, days, days_ago):
    ticket_prices = load_prices(ticker, parse_json=False)
    df = pd.DataFrame.from_records(ticket_prices[-days_ago:], columns=['ds', 'y'])
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=days)
    forecast = m.predict(future)
    dicts = forecast.tail(days*2).to_dict('records')

    for d in dicts:
        d['ds'] = d['ds'].strftime('%Y-%m-%d') if d['ds'] else None

    return dumps(dicts)
