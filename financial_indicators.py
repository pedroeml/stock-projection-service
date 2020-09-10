import re

from collections import OrderedDict
from decimal import Decimal
from http import cookiejar
from lxml.html import fragment_fromstring
from urllib import request, parse

URL = 'http://www.fundamentus.com.br/resultado.php'
HEADERS = [
    ('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201'),
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
        'P/L': str_to_decimal(rows_children[2].text),
        'P/VP': str_to_decimal(rows_children[3].text),
        'PSR': str_to_decimal(rows_children[4].text),
        'DY': str_to_decimal(rows_children[5].text),
        'P/Ativo': str_to_decimal(rows_children[6].text),
        'P/Cap.Giro': str_to_decimal(rows_children[7].text),
        'P/EBIT': str_to_decimal(rows_children[8].text),
        'P/ACL': str_to_decimal(rows_children[9].text),
        'EV/EBIT': str_to_decimal(rows_children[10].text),
        'EV/EBITDA': str_to_decimal(rows_children[11].text),
        'Mrg.Ebit': str_to_decimal(rows_children[12].text),
        'Mrg.Liq.': str_to_decimal(rows_children[13].text),
        'Liq.Corr.': str_to_decimal(rows_children[14].text),
        'ROIC': str_to_decimal(rows_children[15].text),
        'ROE': str_to_decimal(rows_children[16].text),
        'Liq.2meses': str_to_decimal(rows_children[17].text),
        'Pat.Liq': str_to_decimal(rows_children[18].text),
        'Div.Brut/Pat.': str_to_decimal(rows_children[19].text),
        'Cresc.5anos': str_to_decimal(rows_children[20].text),
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
