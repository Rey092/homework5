from abc import ABC, abstractmethod

import requests

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/39.0.2171.95 Safari/537.36'}


class Request(ABC):
    @abstractmethod
    def get(self, url):
        pass


class BasicRequest(Request):
    def get(self, url):
        return requests.get(url, headers=headers)


class ProxyRequest(Request):
    def __init__(self):
        self._parser = BasicRequest()
        self.status_code = None

    def get(self, url):
        result = self._connect(url)
        if result:
            return result

    def get_text(self, url):
        text_data = self.get(url).text
        return text_data

    def _connect(self, url):
        try:
            result = self._parser.get(url)
        except Exception as exp:
            self._logger(exp)
            return None
        else:
            self._logger(f'Connection to {url}.')
            self._check_status(result)
            return result

    def _check_status(self, result):
        try:
            self.status_code = result.status_code
            result.raise_for_status()
        except Exception as err:
            self._logger(err)
            return False
        else:
            self._logger('Status-code: 200.')
            return True

    @staticmethod
    def _logger(msg):
        print(msg)
