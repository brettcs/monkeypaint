# This file is part of Monkeypaint
#   <https://brettcsmith.org/monkeypaint>
# Copyright © 2021 Brett Smith <brettcsmith@brettcsmith.org>
# You may use, share, and modify this software under the terms of the
# GNU Affero General Public License version 3
#   <https://opensource.org/licenses/AGPL-3.0>

import logging

from collections.abc import (
    Callable,
)

from typing import (
    Iterator,
)

import requests
from . import VERSION, Color, logger

HTTPGetFunc = Callable[..., requests.Response]

logger = logger.getChild('colorapi')

class ColorAPIClient:
    HEADERS = requests.utils.default_headers()
    HEADERS['User-Agent'] = f"monkeypaint/{VERSION} ({HEADERS['User-Agent']})"
    URL = 'https://www.thecolorapi.com/scheme'

    def __init__(self, get_func: HTTPGetFunc=requests.get, url: str=URL) -> None:
        self.get_func = get_func
        self.url = url

    def get_palette(self, base_color: Color, count: int, mode: str) -> Iterator[Color]:
        params = {
            'count': count,
            'format': 'json',
            'hex': base_color.hex_format(''),
            'mode': mode,
        }
        response = self.get_func(self.url, headers=self.HEADERS, params=params)
        response.raise_for_status()
        for color_response in response.json()['colors']:
            color_rgb = color_response['rgb']
            yield Color(color_rgb['r'], color_rgb['g'], color_rgb['b'])
