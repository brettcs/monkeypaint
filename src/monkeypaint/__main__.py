# This file is part of Monkeypaint
#   <https://brettcsmith.org/monkeypaint>
# Copyright © 2021 Brett Smith <brettcsmith@brettcsmith.org>
# You may use, share, and modify this software under the terms of the
# GNU Affero General Public License version 3
#   <https://opensource.org/licenses/AGPL-3.0>

import argparse
import configparser
import enum
import itertools
import logging
import logging.config
import os
import random
import signal
import sys
import types

from collections.abc import (
    Iterator,
    Mapping,
    Sequence,
)
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    NoReturn,
    Optional,
    TextIO,
    Type,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from . import colorapi

from . import Color, KeyColorGroups, logger
from requests.exceptions import HTTPError, RequestException

Section = Mapping[str, str]
T = TypeVar('T')

class ConfigurationError(ValueError):
    def __init__(self,
                 error: str,
                 opt_name: Optional[str]=None,
                 sect_name: Optional[str]=None,
                 ) -> None:
        super().__init__(error, opt_name, sect_name)
        self.error = error
        self.opt_name = opt_name
        self.sect_name = sect_name

    def __str__(self) -> str:
        if self.opt_name is None:
            return self.error
        elif self.sect_name is None:
            return f'{self.opt_name!r} {self.error}'
        else:
            return f'{self.opt_name!r} from {self.sect_name} {self.error}'


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
        elif isinstance(exc_value, ConfigurationError):
            msg = f"configuration error: {exc_value}"
            exitcode = os.EX_CONFIG
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


class LogLevel(enum.IntEnum):
    CRIT = logging.CRITICAL
    CRITICAL = CRIT
    DEBUG = logging.DEBUG
    ERROR = logging.ERROR
    FATAL = CRITICAL
    INFO = logging.INFO
    INFORMATION = INFO
    NOTE = INFO
    NOTICE = INFO
    WARN = logging.WARNING
    WARNING = WARN


class Config(configparser.ConfigParser):
    def __init__(self) -> None:
        super().__init__(allow_no_value=True)
        self['ColorAPI'] = {
            'mode': 'analogic',
            'fn mode': 'monochrome',
        }
        self['LogFormatter default'] = {
            'format': '%%(name)s: %%(levelname)s: %%(message)s',
        }
        self['LogHandler default'] = {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        }
        self['Logging'] = {
            'handlers': 'default',
            'level': 'INFO',
        }
        self['Output'] = {
            'path': '-',
        }
        self['Palette'] = {
            'group prefix': 'Group',
            'minimum base': '384',
        }
        self._color_maker: Optional[colorapi.ColorAPIClient] = None

    def _sections_prefixed(self, prefix: str, subslice: Optional[slice]=None) -> Iterator[tuple[str, Section]]:
        if subslice is None:
            subslice = slice(len(prefix), None)
        for key, value in self.items():
            if key.startswith(prefix):
                yield (key[subslice], value)

    @staticmethod
    def parse_minimum_base(s: str, sect_name: str='[Palette]') -> int:
        try:
            base = int(s)
        except ValueError as error:
            raise ConfigurationError(error.args[0], 'minimum base', sect_name)
        else:
            max_base = 255 * 3
            if 0 <= base <= max_base:
                return base
            else:
                raise ConfigurationError(f"not in range 0-{max_base}", 'minimum base', sect_name)

    def get_palette(self, base: Color, count: int, *, fn: bool=False) -> Iterator[Color]:
        if self._color_maker is None:
            from . import colorapi
            self._color_maker = colorapi.ColorAPIClient(
                url=self['ColorAPI'].get('url', colorapi.ColorAPIClient.URL),
            )
        mode = self['ColorAPI']['fn mode' if fn else 'mode']
        return self._color_maker.get_palette(base, count, mode)

    def key_color_groups(self, group_prefix: Optional[str]=None) -> Mapping[str, Section]:
        if group_prefix is None:
            group_prefix = self['Palette']['group prefix']
        groups = dict(
            (key, value)
            for key, section in self._sections_prefixed(group_prefix, slice(None, None))
            if (value := {k: v for k, v in section.items() if v is None})
        )
        if not groups:
            logger.warning(
                "did not find any key groupings defined under the prefix %r",
                group_prefix,
            )
        return groups

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

    def random_base(self, minimum_base: Optional[int]=None) -> Color:
        if minimum_base is None:
            minimum_base = self.parse_minimum_base(self['Palette']['minimum base'])
        minimum_base = min(255 * 3, minimum_base)
        r = random.randint(max(0, minimum_base - 255 * 2), 255)
        g = random.randint(max(0, minimum_base - r - 255), 255)
        b = random.randint(max(0, minimum_base - r - g), 255)
        return Color(r, g, b)

    def setup_logging(self, level: Optional[str]=None, logger: logging.Logger=logger) -> None:
        logger_config = {
            'handlers': self['Logging']['handlers'].split(),
            'level': (self['Logging']['level'] if level is None else level).upper(),
        }
        return logging.config.dictConfig({
            'disable_existing_loggers': False,
            'formatters': dict(self._sections_prefixed('LogFormatter ')),
            'handlers': dict(self._sections_prefixed('LogHandler ')),
            'loggers': {logger.name: logger_config},
            'version': 1,
        })


def parse_arguments(arglist: Optional[Sequence[str]]=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='monkeypaint',
        usage="%(prog)s [-c BASE] [-g GROUP] [other options]",
        description="Generate lighting profiles for the Kinesis Freestyle Edge",
        epilog="""All listed defaults are built into the program, and may be
overridden by your configuration file.""",
    )
    parser.add_argument(
        '--base-color', '--color', '-c',
        metavar='BASE',
        help="Base color for the generated palette. You can specify a number"
        " between 0-765 to pick a random color with at least that much RGB; or"
        " specify a color with a 3- or 6-digit hex color code.",
    )
    parser.add_argument(
        '--configuration-group', '-g',
        metavar='GROUP',
        help="Read key groupings from configuration file sections that start"
        " with this word. Default 'Group'.",
    )
    parser.add_argument(
        '--configuration-file', '-C',
        metavar='PATH',
        help="Path of the configuration file to read",
    )
    parser.add_argument(
        '--log-level', '--loglevel',
        metavar='LEVEL',
        help="Show log messages at this level and above."
        " Choices are debug, info, warning, error, and critical."
        " Default info.",
    )
    parser.add_argument(
        '--output-file', '-O',
        metavar='PATH',
        help="Path of the lighting profile output. Default stdout.",
    )
    args = parser.parse_args()

    if args.configuration_file is None:
        import appdirs  # type:ignore[import]
        config_dirs: list[Path] = []
        if xdg_config_dirs := os.environ.get('XDG_CONFIG_DIRS'):
            xdg_config_paths = [Path(s, 'monkeypaint') for s in xdg_config_dirs.split(':')]
            config_dirs.extend(p for p in xdg_config_paths if p.is_absolute())
        config_dirs.append(Path(appdirs.user_config_dir('monkeypaint', roaming=True)))
        for dir_path in config_dirs:
            config_path = dir_path / 'config.ini'
            if config_path.exists():
                args.configuration_file = config_path
                break
        else:
            args.configuration_file = os.devnull

    if args.log_level is not None:
        try:
            args.log_level = LogLevel[args.log_level.upper()].name
        except KeyError:
            parser.error(f"unknown log level {args.log_level!r}")

    args.int_base = None
    args.hex_base = None
    if args.base_color is not None:
        try:
            args.int_base = Config.parse_minimum_base(args.base_color, 'arguments')
        except ConfigurationError as error:
            try:
                args.hex_base = Color.from_hex(args.base_color)
            except ValueError:
                parser.error(f"base color {args.base_color!r} is not hex or a minimum color")

    return args

def main(arglist: Optional[Sequence[str]]=None, main_logger: Optional[logging.Logger]=None) -> int:
    args = parse_arguments(arglist)
    config = Config()
    with open(args.configuration_file) as conffile:
        config.read_file(conffile)
    if main_logger is not None:
        config.setup_logging(args.log_level, main_logger)
    logger.debug("read configuration file %s", args.configuration_file)

    base_color: Color = args.hex_base or config.random_base(args.int_base)
    color_groups = KeyColorGroups.from_config(config.key_color_groups(args.configuration_group))
    logger.info("generating a palette from %s with %s colors",
                base_color, color_groups.group_count)
    with config.output_file(args.output_file) as out_file:
        for fn in (False, True):
            colors = config.get_palette(base_color, color_groups.group_count, fn=fn)
            for line in color_groups.led_lines(colors, fn=fn):
                out_file.write(line)
    return os.EX_OK

def entry_point(arglist: Optional[Sequence[str]]=None) -> int:
    sys.excepthook = ExceptHook()
    return main(arglist, logging.getLogger())

if __name__ == '__main__':
    exit(entry_point())
