import ssl
from functools import wraps

import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache
from fake_useragent import FakeUserAgent

# unblocking checking certs https
ssl._create_default_https_context = ssl._create_unverified_context

cache = TTLCache(maxsize=10_000_000, ttl=360)


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
        _table_head = tuple(
            head.get_text().encode("ascii", 'ignore').decode('utf-8').replace(',', '')
            for head in raw_data.find('table', id=table_data).find('thead').find_all("th")
        )
        return tuple(
            dict(zip(_table_head, [doc.get_text().strip() for doc in td.find_all("td")]))
            for td in raw_data.find('tbody').find_all("tr")
        )

    @staticmethod
    def parse_data_summary(raw_data: BeautifulSoup) -> dict:
        """Parse data summary for all cases
        :param raw_data:
        :return:
        """
        return dict(
            zip(
                ('Cases', 'Dead', 'Recoverd'), tuple(
                    doc.find('span').get_text().strip()
                    for doc in raw_data.find_all('div', id='maincounter-wrap')
                )
            )
        )


class Api(Helper):

    def __init__(self):
        self.__url = 'https://www.worldometers.info/coronavirus/'
        self.__agent = FakeUserAgent()
        Helper.__init__(self)

    @cache_api
    def _fetch_data(self) -> BeautifulSoup:
        response = requests.get(self.__url, headers={'User-Agent': self.__agent.random})
        return BeautifulSoup(response.text, "html.parser")

    def fetch_summary_data(self) -> dict:
        """Fetch summary data
        :return: tuple
        """
        return dict(
            zip(
                ('Cases', 'Dead', 'Recoverd'), tuple(
                    doc.find('span').get_text().strip()
                    for doc in self._fetch_data().find_all('div', id='maincounter-wrap')
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
