import re

from collections import OrderedDict
from decimal import Decimal
from http import cookiejar
from lxml.html import fragment_fromstring
from os import environ
from urllib import request, parse


def get_url():
    env = environ.get('FLASK_ENV', 'development')

    if env == 'development':
        url = 'https://www.fundamentus.com.br/resultado.php'
    else:
        phproxy = 'https://cin.ufpe.br/~bifm/tools/proxy/index.php'
        url = phproxy + '?q=https%3A%2F%2Fwww.fundamentus.com.br%2Fresultado.php&hl=180'

    return url


URL = get_url()
HEADERS = [
    ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'),
    ('Accept', 'text/html, text/plain, text/css, text/sgml, */*;q=0.01')
]
SEARCH_PARAMS = {
    'pl_min': '',
    'pl_max': '',
    'pvp_min': '',
    'pvp_max': '',
    'psr_min': '',
    'psr_max': '',
    'divy_min': '',
    'divy_max': '',
    'pativos_min': '',
    'pativos_max': '',
    'pcapgiro_min': '',
    'pcapgiro_max': '',
    'pebit_min': '',
    'pebit_max': '',
    'fgrah_min': '',
    'fgrah_max': '',
    'firma_ebit_min': '',
    'firma_ebit_max': '',
    'margemebit_min': '',
    'margemebit_max': '',
    'margemliq_min': '',
    'margemliq_max': '',
    'liqcorr_min': '',
    'liqcorr_max': '',
    'roic_min': '',
    'roic_max': '',
    'roe_min': '',
    'roe_max': '',
    'liq_min': '',
    'liq_max': '',
    'patrim_min': '',
    'patrim_max': '',
    'divbruta_min': '',
    'divbruta_max': '',
    'tx_cresc_rec_min': '',
    'tx_cresc_rec_max': '',
    'setor': '',
    'negociada': 'ON',
    'ordem': '1',
    'x': '28',
    'y': '16',
}


def change_decimal_separator(str_number):
    return str_number.replace('.', '').replace(',', '.')


def str_to_decimal(str_number):
    str_international = change_decimal_separator(str_number)

    return Decimal(str_international[:-1]) / 100 if str_international.endswith('%') else Decimal(str_international)


def build_indicators_dict(rows_children):
    return {
        'Cotacao': str_to_decimal(rows_children[1].text),
        'PL': str_to_decimal(rows_children[2].text),
        'PVP': str_to_decimal(rows_children[3].text),
        'PSR': str_to_decimal(rows_children[4].text),
        'DY': str_to_decimal(rows_children[5].text),
        'PAtivo': str_to_decimal(rows_children[6].text),
        'PCapGiro': str_to_decimal(rows_children[7].text),
        'PEBIT': str_to_decimal(rows_children[8].text),
        'PACL': str_to_decimal(rows_children[9].text),
        'EVEBIT': str_to_decimal(rows_children[10].text),
        'EVEBITDA': str_to_decimal(rows_children[11].text),
        'MrgEbit': str_to_decimal(rows_children[12].text),
        'MrgLiq': str_to_decimal(rows_children[13].text),
        'LiqCorr': str_to_decimal(rows_children[14].text),
        'ROIC': str_to_decimal(rows_children[15].text),
        'ROE': str_to_decimal(rows_children[16].text),
        'Liq2meses': str_to_decimal(rows_children[17].text),
        'PatLiq': str_to_decimal(rows_children[18].text),
        'DivBrutPat': str_to_decimal(rows_children[19].text),
        'Cresc5anos': str_to_decimal(rows_children[20].text),
    }


def load_indicators():
    cookie_jar = cookiejar.CookieJar()
    opener = request.build_opener(request.HTTPCookieProcessor(cookie_jar))
    opener.addheaders = HEADERS

    with opener.open(URL, parse.urlencode(SEARCH_PARAMS).encode('UTF-8')) as link:
        content = link.read().decode('ISO-8859-1')

    pattern = re.compile('<table id="resultado".*</table>', re.DOTALL)
    content = re.findall(pattern, content)[0]
    page = fragment_fromstring(content)
    indicators = OrderedDict()

    for rows in page.xpath('tbody')[0].findall("tr"):
        indicators.update({
            rows.getchildren()[0][0].getchildren()[0].text: build_indicators_dict(rows.getchildren())
        })

    return indicators
