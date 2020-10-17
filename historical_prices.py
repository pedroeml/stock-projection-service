from gzip import decompress
from http import cookiejar
from json import loads, dumps
from os import environ
from time import strftime, gmtime
from urllib import request


def get_url(ticker):
    env = environ.get('FLASK_ENV', 'development')

    if env == 'development':
        url = 'https://www.fundamentus.com.br/amline/cot_hist.php?papel='
    else:
        phproxy = 'https://cin.ufpe.br/~bifm/tools/proxy/index.php'
        url = phproxy + '?q=https%3A%2F%2Fwww.fundamentus.com.br%2Famline%2Fcot_hist.php%3Fpapel%3D'

    return url + ticker + '&hl=1a7'


def build_headers(url):
    return [
        ('Accept', 'application/json, text/javascript, */*; q=0.01'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Referer', url),
        ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'),
    ]


def parse_epoch_time(parsed_content):
    return [[strftime('%Y-%m-%d', gmtime(unix_epoch_time/1000)), price] for [unix_epoch_time, price] in parsed_content]


def load_prices(ticker, parse_json=True):
    url = get_url(ticker)
    cookie_jar = cookiejar.CookieJar()
    opener = request.build_opener(request.HTTPCookieProcessor(cookie_jar))
    opener.addheaders = build_headers(url)

    with opener.open(url) as link:
        gzip_response = link.read()
        binary_response = decompress(gzip_response)
        parsed_content = loads(binary_response)
        content = parse_epoch_time(parsed_content)

    return dumps(content) if parse_json else content
