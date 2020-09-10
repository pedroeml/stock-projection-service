from http import cookiejar
from os import environ
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
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
        ('Referer', url),
        ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'),
    ]


def load_prices(ticker):
    url = get_url(ticker)
    cookie_jar = cookiejar.CookieJar()
    opener = request.build_opener(request.HTTPCookieProcessor(cookie_jar))
    opener.addheaders = build_headers(url)

    with opener.open(url) as link:
        content = link.read().decode()

    return content
