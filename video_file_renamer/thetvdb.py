import requests
import functools
import logging
import os
import json
import datetime

from typing import Callable

from .settings import TOKEN_STORE

logger = logging.getLogger('vfr.thetvdb')


class TokenHandler:
    def __init__(self,
                 name: str,
                 get_token: Callable,
                 token_store: str = TOKEN_STORE):
        self.name = name
        self.get_token = get_token
        self.token_store = token_store
        self.token = None

    def _get_saved_token(self):
        if not os.path.exists(self.token_store):
            raise FileNotFoundError(f"The token_store doesn't exist")

        with open(self.token_store) as ts:
            data = json.load(ts)

        token_date = datetime.datetime.fromtimestamp(data['timestamp'])
        now = datetime.datetime.now()
        timedelta = datetime.timedelta(hours=24)
        if now-timedelta <= token_date <= now:
            logger.debug("Saved token still valid")
            return data['token']
        else:
            logger.debug("Saved token is not valid")
            raise Exception("Token out of date")

    def _save_token(self, token, update_store=True):
        if not os.path.exists(os.path.dirname(self.token_store)):
            raise FileNotFoundError(
                f"The directory {os.path.dirname(self.token_store)} "
                f"doesn't exists")
        if update_store:
            with open(self.token_store, 'w') as ts:
                json.dump({
                    "token": token,
                    "timestamp": datetime.datetime.now().timestamp()
                }, ts)
            logger.debug('Token saved in token_store')
        self.token = token
        logger.debug('Token set in TokenHandler')

    @staticmethod
    def _logged_in(func: Callable):
        @functools.wraps(func)
        def wrapper_logged_in(self, *args, **kwargs):
            if self.token is None:
                try:
                    self._save_token(
                        self._get_saved_token(),
                        update_store=False)
                except FileNotFoundError or Exception as e:
                    logger.debug(e)
                    self._save_token(self.get_token())
            return func(self, *args, **kwargs)
        return wrapper_logged_in


class TheTVDB(TokenHandler):
    def __init__(self, apikey: str, **kwargs):
        TokenHandler.__init__(self, 'thetvdb', self.get_token_from_apikey)
        self.url = 'https://api.thetvdb.com'
        self.apikey = apikey
        # Kwargs
        if kwargs.get("url"):
            self.url = kwargs["url"]

    def get_token_from_apikey(self):
        login_url = f'{self.url}/login'

        response = requests.post(
            url=login_url,
            json={"apikey": self.apikey})

        _json = response.json()

        if "Error" in _json:
            raise Exception(
                f"API responded with Error: {_json['Error']}")

        logger.debug("Successfully got TheTVDB token")
        return _json['token']

    @TokenHandler._logged_in
    def search_series(self, name: str) -> dict:
        logger.debug(f"Fetching series detail for {name}")

        url_path = f"{self.url}/search/series"

        response = requests.get(
            url=url_path,
            headers={"Authorization": f"Bearer {self.token}"},
            params={"name": name}
        )

        _json = response.json()

        return _json

    @TokenHandler._logged_in
    def series_id_episodes(self, id: int) -> dict:
        logger.debug(f"Fetching all episodes for series id {id}")

        url_path = f"{self.url}/series/{id}/episodes"

        response = requests.get(
            url=url_path,
            headers={"Authorization": f"Bearer {self.token}"}
        )

        _json = response.json()

        if _json['links']['next'] is not None:
            response = requests.get(
                url=url_path,
                headers={"Authorization": f"Bearer {self.token}"},
                params={"page": _json['links']['next']}
            ).json()['data']
            for item in response:
                _json['data'].append(item)

        return _json
