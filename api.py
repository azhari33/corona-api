import orjson
import ssl
from functools import wraps
import concurrent.futures
import pandas as pd
import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache
from fake_useragent import FakeUserAgent

# unblocking checking certs https
ssl._create_default_https_context = ssl._create_unverified_context

cache = TTLCache(maxsize=100_000, ttl=600)


def cache_api(f):
    @wraps(f)
    def cache_response(*args, **kwargs):
        if cache.get(f.__name__, None) is None:
            cache[f.__name__] = f(*args, **kwargs)
        return cache[f.__name__]

    return cache_response


class Helper:

    @staticmethod
    def parse_data_by_country(raw_data: BeautifulSoup, table_data: str) -> tuple:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            _table_head = tuple(
                executor.map(
                    lambda x: x.get_text().encode("ascii", 'ignore').decode('utf-8').replace(',', ''),
                    raw_data.find('table', id=table_data).find('thead').find_all("th")
                )
            )
            return tuple(
                map(
                    lambda x: dict(zip(_table_head, tuple(
                        executor.map(lambda y: y.get_text().strip(), x.find_all("td"))
                    ))),
                    raw_data.find('tbody').find_all("tr")
                )
            )

    @staticmethod
    def parse_data_summary(raw_data: BeautifulSoup) -> dict:
        """Parse data summary for all cases
        :param raw_data:
        :return:
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            return dict(
                zip(
                    ('Cases', 'Dead', 'Recovered'), tuple(
                        executor.map(
                            lambda x: x.find('span').get_text().strip(), raw_data.find_all('div', id='maincounter-wrap')
                        )
                    )
                )
            )


class Api(Helper):

    def __init__(self):
        self.__url_live = 'https://www.worldometers.info/coronavirus/'
        self.__url_history = 'https://covid.ourworldindata.org/data/ecdc/full_data.csv'
        self.__agent = FakeUserAgent()
        Helper.__init__(self)

    @cache_api
    def _fetch_data(self) -> BeautifulSoup:
        response = requests.get(self.__url_live, headers={'User-Agent': self.__agent.random})
        return BeautifulSoup(response.text, "html.parser")

    @cache_api
    def _fetch_history_data(self) -> pd:
        return pd.read_csv(self.__url_history)

    def fetch_summary_data(self) -> dict:
        """Fetch summary data
        :return: tuple
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            return dict(
                zip(
                    ('Cases', 'Dead', 'Recover'), tuple(
                        executor.map(
                            lambda x: x.find('span').get_text().strip(),
                            self._fetch_data().find_all('div', id='maincounter-wrap')
                        )
                    )
                )
            )

    def fetch_current_data(self) -> tuple:
        """Fetch current latest data
        :return: tuple
        """
        return self.parse_data_by_country(self._fetch_data(), 'main_table_countries_today')

    def fetch_yesterday_data(self) -> tuple:
        """Fetch yesterday data
        :return: tuple
        """
        return self.parse_data_by_country(self._fetch_data(), 'main_table_countries_yesterday')

    def fetch_history_data(self, date: str = None, country: str = None) -> tuple:
        """Fetch data history based on filter
        :param date: str
        :param country: str
        :return:tuple
        """
        df = self._fetch_history_data()
        if date is not None:
            df = df[df['date'] == date]
        if country is not None:
            df = df[df['location'] == country]
        return orjson.loads(df.to_json(orient='records'))
