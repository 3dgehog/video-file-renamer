import requests
import functools
import logging

logger = logging.getLogger('vfr.thetvdb')


def _logged_in(func):
    @functools.wraps(func)
    def wrapper_logged_in(self, *args, **kwargs):
        if self.token is None:
            self.login()
        return func(self, *args, **kwargs)
    return wrapper_logged_in


class TheTVDB():
    def __init__(self, apikey: str, **kwargs):
        self.url = 'https://api.thetvdb.com'
        self.apikey = apikey
        self.token = None
        # Kwargs
        if kwargs.get("url"):
            self.url = kwargs.get("url")

    def login(self) -> dict:
        login_url = f'{self.url}/login'

        response = requests.post(
            url=login_url,
            json={"apikey": self.apikey})

        _json = response.json()

        if "Error" in _json:
            raise Exception(
                f"API responded with Error: {_json['Error']}")

        self.token = _json['token']
        logger.debug("Successfully got TheTVDB token")
        return _json

    @_logged_in
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

    @_logged_in
    def series_id_episodes(self, id: int) -> dict:
        logger.debug(f"Fetching all episodes for series id {id}")

        url_path = f"{self.url}/series/{id}/episodes"

        response = requests.get(
            url=url_path,
            headers={"Authorization": f"Bearer {self.token}"},
            params={}
        )

        _json = response.json()

        if _json['links']['next'] is not None:
            _json['data'].append(
                requests.get(
                    url=url_path,
                    headers={"Authorization": f"Bearer {self.token}"},
                    params={"page": _json['links']['next']}
                ).json()['data']
            )

        return _json
