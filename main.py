import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
cache = TTLCache(maxsize=10_000_000, ttl=360)


def get_data(table_data: str):
    if cache.get(table_data, None) is None:
        url = 'https://www.worldometers.info/coronavirus/'
        # fake agent
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        cache[table_data] = soup.find('table', id=table_data)
    return cache.get(table_data)


def parse_data(raw_data: str) -> list:
    _table_head = tuple(
        head.get_text().encode("ascii", 'ignore').decode('utf-8').replace(',', '')
        for head in raw_data.find('thead').find_all("th")
    )
    return [
        dict(zip(_table_head, [doc.get_text().strip() for doc in td.find_all("td")]))
        for td in raw_data.find('tbody').find_all("tr")
    ]


@app.get("/")
def request_data():
    _raw_data = get_data('main_table_countries_today')
    return parse_data(_raw_data)


@app.get("/now")
def current_data():
    _raw_data = get_data('main_table_countries_today')
    return parse_data(_raw_data)


@app.get("/yesterday")
def yesterday_data():
    _raw_data = get_data('main_table_countries_yesterday')
    return parse_data(_raw_data)
