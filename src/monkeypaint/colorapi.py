import logging

from collections.abc import (
    Callable,
)

from typing import (
    Iterator,
)

import requests
from . import Color, logger

HTTPGetFunc = Callable[..., requests.Response]

logger = logger.getChild('colorapi')

class ColorAPIClient:
    HEADERS = requests.utils.default_headers()
    HEADERS['User-Agent'] = f"monkeypaint/0.1 ({HEADERS['User-Agent']})"
    URL = 'https://www.thecolorapi.com/scheme'

    def __init__(self, get_func: HTTPGetFunc=requests.get, url: str=URL) -> None:
        self.get_func = get_func
        self.url = url

    def get_palette(self, seed: Color, count: int, mode: str) -> Iterator[Color]:
        params = {
            'count': count,
            'format': 'json',
            'hex': seed.hex_format(''),
            'mode': mode,
        }
        response = self.get_func(self.url, headers=self.HEADERS, params=params)
        response.raise_for_status()
        for color_response in response.json()['colors']:
            color_rgb = color_response['rgb']
            yield Color(color_rgb['r'], color_rgb['g'], color_rgb['b'])
