import guessit
import logging

from typing import Union

logger = logging.getLogger('vfr.utils')


def get_guessit(name: str) -> Union[dict, None]:
    guessitmatch = dict(guessit.guessit(name))

    if 'title' not in guessitmatch:
        logger.warning(f"Unable to find title for: '{name}'")
        return None

    return guessitmatch
