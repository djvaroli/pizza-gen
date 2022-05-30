import shutil
import sys
from pathlib import Path

import requests
from loguru import logger
from requests.exceptions import InvalidURL


def _level_filter(level: str):
    """Returns a callable for filtering logs of a specified level.

    Args:
        level (str): name of level to filter for. Can be 'debug', 'info', 'warning', 'error'

    Raises:
        ValueError: if invalid logging level is specified.
    """

    valid_levels = ["debug", "info", "warning", "error"]
    if level not in valid_levels:
        raise ValueError(f"Level must be one of {valid_levels}, got {level}.")

    def level_filter_function(record):
        return record["level"].name == level.upper()

    return level_filter_function


logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<yellow>{time}</yellow> <red>{message}</red>",
    filter=_level_filter("error"),
)
logger.add(
    sys.stdout,
    colorize=True,
    format="<yellow>{time}</yellow> <green>{message}</green>",
    filter=_level_filter("info"),
)


def download_image(url: str, filename: str):
    """Downloads an image from a url to local disk under the specified file name.

    Args:
        url (str): remote location of the image file.
        filename (str): name of file to save image under on local disk.
    """
    try:
        r = requests.get(url, stream=True)
    except InvalidURL as e:
        logger.error(
            f"Could not download image {filename}. An invalid URL was provided. {e}."
        )
        return

    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        with open(filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)

        logger.info(f"Image `{filename}` successfully downloaded.")
    else:
        logger.error(
            f"Could not download image {filename}. Received {r.status_code} status code."
        )
