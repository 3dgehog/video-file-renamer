import os
import difflib

from .thetvdb import TheTVDB
from .settings import VALID_EXTENSIONS
from .utils import get_guessit


class App():
    def __init__(self, apikey: str):
        self.thetvdb = TheTVDB(apikey=apikey)

    def scan_folder(self, path: str):
        if not os.path.exists(path):
            raise FileExistsError(f"{path} doesn't exists")
        if not os.path.isdir(path):
            raise NotADirectoryError

        sources = []
        for entry in os.scandir(path):
            if entry.name.rpartition('.')[-1] not in VALID_EXTENSIONS:
                continue
            sources.insert(0, {"name": entry.name, "path": entry.path})

        for entry in sources:
            guessit_match = get_guessit(entry['name'])
            entry["guessit"] = guessit_match

        series_names = []
        for entry in sources:
            entry['match'] = {}
            diff_match = difflib.get_close_matches(
                entry['guessit']['title'],
                series_names,
                n=1, cutoff=0.9)
            if not diff_match:
                series_names.append(entry['guessit']['title'])
                entry['match']['name'] = entry['guessit']['title']
            else:
                entry['match']['name'] = diff_match[0]

        for serie in series_names:
            id = self.thetvdb.search_series(serie)['data'][0]['id']
            results = self.thetvdb.series_id_episodes(id)

            for entry in sources:
                if entry['match']['name'] == serie:
                    entry['thetvdb'] = next(
                        x for x in results['data'] if
                        x['airedSeason'] ==
                        entry['guessit']['season']
                        and x['airedEpisodeNumber'] ==
                        entry['guessit']['episode'])

        for entry in sources:
            entry['new_name'] = (f"{entry['match']['name']}"
                                 f" - S{entry['thetvdb']['airedSeason']:02}E"
                                 f"{entry['thetvdb']['airedEpisodeNumber']:02}"
                                 f" - {entry['thetvdb']['episodeName']}"
                                 f".{entry['guessit']['container']}")

        for entry in sources:
            print(
                f"{'From:':>5} {entry['name']:<}\n"
                f"{'To:':>5} {entry['new_name']:<}\n")

        answer = input("Do you want to rename all files [y|n]: ")

        if answer == 'y':
            print("renaming")
            for entry in sources:
                os.rename(
                    entry['path'], os.path.join(
                        os.path.dirname(entry['path']),
                        entry['new_name']))
        else:
            print("next time!")
