import argparse
import configparser
import itertools
import logging
import os
import random
import signal
import sys
import types

from typing import (
    TYPE_CHECKING,
    Iterator,
    NoReturn,
    Optional,
    Sequence,
    TextIO,
    Type,
    Union,
)

if TYPE_CHECKING:
    from . import colorapi

from . import Color, KeyColorGroups, logger
from requests.exceptions import HTTPError, RequestException

class ExceptHook:
    def __init__(self, logger: logging.Logger=logger, level: int=logging.CRITICAL) -> None:
        self.logger = logger
        self.loglevel = level

    def __call__(self,
                 exc_type: Type[BaseException],
                 exc_value: BaseException,
                 exc_tb: types.TracebackType,
    ) -> NoReturn:
        if isinstance(exc_value, HTTPError):
            msg = "HTTP error: {req.method} {req.url}: {res.reason} ({res.status_code})".format(
                req=exc_value.request,
                res=exc_value.response,
            )
            status_code = exc_value.response.status_code or -1
            exitcode = os.EX_TEMPFAIL if 500 <= status_code < 600 else os.EX_UNAVAILABLE
        elif isinstance(exc_value, RequestException):
            msg = "HTTP {name} on {req.method} {req.url}".format(
                name=exc_type.__name__,
                req=exc_value.request,
            )
            exitcode = os.EX_TEMPFAIL
        elif isinstance(exc_value, OSError):
            msg = "I/O error: {e.filename}: {e.strerror}".format(e=exc_value)
            exitcode = os.EX_IOERR
        elif isinstance(exc_value, KeyboardInterrupt):
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            os.kill(0, signal.SIGINT)
            signal.pause()
        else:
            msg = ": ".join([f"internal {exc_type.__name__}", *exc_value.args])
            exitcode = os.EX_SOFTWARE
        self.logger.log(self.loglevel, msg, exc_info=self.logger.isEnabledFor(logging.DEBUG))
        os._exit(exitcode)


class Config(configparser.ConfigParser):
    def __init__(self) -> None:
        super().__init__(allow_no_value=True)
        self['ColorAPI'] = {
            'mode': 'analogic',
            'fn mode': 'monochrome',
        }
        self['Output'] = {
            'path': '-',
        }
        self['Palette'] = {
            'minimum seed': '192',
        }
        self._color_maker: Optional[colorapi.ColorAPIClient] = None

    def get_palette(self, seed: Color, count: int, *, fn: bool=False) -> Iterator[Color]:
        if self._color_maker is None:
            from . import colorapi
            self._color_maker = colorapi.ColorAPIClient(
                url=self['ColorAPI'].get('url', colorapi.ColorAPIClient.URL),
            )
        mode = self['ColorAPI']['fn mode' if fn else 'mode']
        return self._color_maker.get_palette(seed, count, mode)

    def output_file(self, path_str: Optional[str], stdout_fd: Optional[int]=None) -> TextIO:
        if path_str is None:
            path_str = self['Output']['path']
        if path_str == '-':
            if stdout_fd is None:
                stdout_fd = sys.stdout.fileno()
            open_arg: Union[int, str] = stdout_fd
            closefd = False
        else:
            open_arg = path_str
            closefd = True
        return open(open_arg, 'w', closefd=closefd, encoding='ascii', newline='\r\n')

    def random_seed(self, minimum_seed: Optional[int]=None) -> Color:
        if minimum_seed is None:
            minimum_seed = int(self['Palette']['minimum seed'])
        minimum_seed = min(255 * 3, minimum_seed)
        r = random.randint(max(0, minimum_seed - 255 * 2), 255)
        g = random.randint(max(0, minimum_seed - r - 255), 255)
        b = random.randint(max(0, minimum_seed - r - g), 255)
        return Color(r, g, b)


def parse_arguments(arglist: Optional[Sequence[str]]=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--configuration-file', '--config-file', '-C',
        default=os.path.expanduser('~/.config/monkeypaint/config.ini'),
    )
    parser.add_argument(
        '--output-file', '-O',
    )
    parser.add_argument(
        'seed',
        nargs='?',
    )
    args = parser.parse_args()
    args.int_seed = None
    args.hex_seed = None
    if args.seed is not None:
        try:
            seed = int(args.seed)
        except ValueError:
            hex_seed = True
        else:
            hex_seed = not (0 <= seed <= (255 * 3))
        if hex_seed:
            try:
                args.hex_seed = Color.from_hex(args.seed)
            except ValueError:
                parser.error(f"seed color {args.seed!r} is not hex or a minimum color")
        else:
            args.int_seed = seed
    return args

def main(arglist: Optional[Sequence[str]]=None) -> int:
    args = parse_arguments(arglist)
    config = Config()
    with open(args.configuration_file) as conffile:
        config.read_file(conffile)

    seed_color: Color = args.hex_seed or config.random_seed(args.int_seed)
    color_groups = KeyColorGroups.from_config(config)
    logger.info("generating a palette from %s with %s colors",
                seed_color, color_groups.group_count)
    with config.output_file(args.output_file) as out_file:
        for fn in (False, True):
            colors = config.get_palette(seed_color, color_groups.group_count, fn=fn)
            for line in color_groups.led_lines(colors, fn=fn):
                out_file.write(line)
    return os.EX_OK

if __name__ == '__main__':
    sys.excepthook = ExceptHook()
    exit(main())
