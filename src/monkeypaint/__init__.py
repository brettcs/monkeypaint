# This file is part of Monkeypaint
#   <https://brettcsmith.org/monkeypaint>
# Copyright © 2021 Brett Smith <brettcsmith@brettcsmith.org>
# You may use, share, and modify this software under the terms of the
# GNU Affero General Public License version 3
#   <https://opensource.org/licenses/AGPL-3.0>

import collections
import enum
import logging
import string

from collections.abc import (
    Callable,
    Collection,
    Mapping,
    Sequence,
)

from typing import (
    Any,
    Iterable,
    Iterator,
    NamedTuple,
    Optional,
)

Key = str
KeyGroup = str

logger = logging.getLogger('monkeypaint')

class _Version(NamedTuple):
    major: int
    minor: int
    micro: int = 0

    def __str__(self) -> str:
        return '.'.join(str(n) for n in self)
VERSION = _Version(1, 0, 2)

KEY_ORDER: Sequence[Key] = [
    'hk0',
    'esc',
    *(f'F{n}' for n in range(1, 13)),
    'prnt',
    'pause',
    'del',
    'hk1',
    'hk2',
    'tilde',
    *'1234567890',
    'hyph',
    '=',
    'bspc',
    'home',
    'hk3',
    'hk4',
    'tab',
    *'qwertyuiop',
    'obrk',
    'cbrk',
    '\\',
    'end',
    'hk5',
    'hk6',
    'caps',
    *'asdfghjkl',
    'colon',
    'apos',
    'ent',
    'pup',
    'hk7',
    'hk8',
    'lshft',
    *'zxcvbnm',
    'com',
    'per',
    '/',
    'rshft',
    'up',
    'pdn',
    'hk9',
    'hk10',
    'lctrl',
    'lwin',
    'lalt',
    'lspc',
    'rspc',
    'ralt',
    'rctrl',
    'lft',
    'dwn',
    'rght',
]
KEY_SET = frozenset(KEY_ORDER)

class KeyAliases(enum.Enum):
    act = frozenset({'esc', 'prnt', 'pause', 'lwin'})
    action = act
    actions = act
    alnum = frozenset(string.ascii_lowercase + string.digits)
    alpha = frozenset(string.ascii_lowercase)
    alphabet = alpha
    alphanum = alnum
    alphanumeric = alnum
    apostrophe = frozenset({'apos'})
    arrow = frozenset({'up', 'lft', 'dwn', 'rght'})
    arrows = arrow
    backlight = frozenset({'hk10'})
    backslash = frozenset('\\')
    backspace = frozenset({'bspc'})
    bslash = backslash
    cbrace = frozenset({'cbrk'})
    cbracket = cbrace
    closebrace = cbrace
    closebracket = cbrace
    comma = frozenset({'com'})
    dash = frozenset({'hyph'})
    digit = frozenset(string.digits)
    digits = digit
    dot = frozenset({'per'})
    down = frozenset({'dwn'})
    downarrow = down
    edit = frozenset({'tab', 'bspc', 'del', 'ent'})
    editing = edit
    edits = edit
    enter = frozenset({'ent'})
    eq = frozenset('=')
    equal = eq
    equals = eq
    f1 = frozenset({'F1'})
    f2 = frozenset({'F2'})
    f3 = frozenset({'F3'})
    f4 = frozenset({'F4'})
    f5 = frozenset({'F5'})
    f6 = frozenset({'F6'})
    f7 = frozenset({'F7'})
    f8 = frozenset({'F8'})
    f9 = frozenset({'F9'})
    f10 = frozenset({'F10'})
    f11 = frozenset({'F11'})
    f12 = frozenset({'F12'})
    fn = frozenset({'hk9'})
    forwardslash = frozenset('/')
    func = frozenset(f'F{n}' for n in range(1, 13))
    function = func
    fslash = forwardslash
    grave = frozenset({'tilde'})
    hot = frozenset(f'hk{n}' for n in range(11))
    hotkey = hot
    hotkey0 = frozenset({'hk0'})
    hotkey1 = frozenset({'hk1'})
    hotkey2 = frozenset({'hk2'})
    hotkey3 = frozenset({'hk3'})
    hotkey4 = frozenset({'hk4'})
    hotkey5 = frozenset({'hk5'})
    hotkey6 = frozenset({'hk6'})
    hotkey7 = frozenset({'hk7'})
    hotkey8 = frozenset({'hk8'})
    hotkeys = hot
    hyphen = dash
    led = backlight
    left = frozenset({'lft'})
    leftarrow = left
    light = backlight
    lshift = frozenset({'lshft'})
    lspace = frozenset({'lspc'})
    macro = hot
    macros = hot
    meta = frozenset({'caps', 'lshft', 'rshft', 'lctrl', 'rctrl', 'lalt', 'ralt'})
    nav = frozenset({'home', 'end', 'pup', 'pdn'})
    navigation = nav
    number = digit
    numbers = digit
    obrace = frozenset({'obrk'})
    obracket = obrace
    openbrace = obrace
    openbracket = obrace
    period = dot
    pagedown = frozenset({'pdn'})
    pagedn = pagedown
    pageup = frozenset({'pup'})
    pgdn = pagedown
    pgdown = pagedown
    pgup = pageup
    prtsc = frozenset({'prnt'})
    prtscr = prtsc
    punc = frozenset({
        'tilde', 'hyph', '=',
        'obrk', 'cbrk', '\\',
        'colon', 'apos',
        'com', 'per', '/',
    })
    punct = punc
    punctuation = punc
    quote = apostrophe
    right = frozenset({'rght'})
    rightarrow = right
    row1 = frozenset(KEY_ORDER[0:17])
    row2 = frozenset(KEY_ORDER[17:34])
    row3 = frozenset(KEY_ORDER[34:51])
    row4 = frozenset(KEY_ORDER[51:67])
    row5 = frozenset(KEY_ORDER[67:83])
    row6 = frozenset(KEY_ORDER[83:])
    rshift = frozenset({'rshft'})
    rspace = frozenset({'rspc'})
    space = frozenset({'lspc', 'rspc'})
    uparrow = frozenset({'up'})
    win = frozenset({'lwin'})
    windows = win


class Color(NamedTuple):
    red: int
    green: int
    blue: int

    @classmethod
    def from_hex(cls, s: str) -> 'Color':
        s = s.removeprefix('#')
        step, rem = divmod(len(s), 3)
        if rem or not 1 <= step <= 2:
            raise ValueError("color must be 3 or 6 hex characters")
        rep = 3 - step
        r = int(s[step * 0:step * 1] * rep, 16)
        g = int(s[step * 1:step * 2] * rep, 16)
        b = int(s[step * 2:step * 3] * rep, 16)
        return cls(r, g, b)

    def __str__(self) -> str:
        return self.hex_format()

    def freestyle_format(self, key: Optional[Key]=None, *, fn: bool=False) -> str:
        retval = f'[{self.red}][{self.green}][{self.blue}]'
        if key is None:
            return retval
        else:
            return f'{"fn " if fn else ""}[{key}]>{retval}\n'

    def hex_format(self, prefix: str='#') -> str:
        return f'{prefix}{self.red:02x}{self.green:02x}{self.blue:02x}'


class KeyColorGroups:
    DEFAULT_CONFIG = {
        'Primary': [KeyAliases.alphanumeric.name, KeyAliases.punctuation.name, KeyAliases.space.name],
        'Secondary': [KeyAliases.editing.name, KeyAliases.function.name, KeyAliases.meta.name],
        'Tertiary': [KeyAliases.hotkeys.name, KeyAliases.navigation.name],
        'Special': [KeyAliases.actions.name, KeyAliases.arrows.name],
    }

    def __init__(self,
                 color_groups: Mapping[KeyGroup, Sequence[Key]],
                 unassigned_pre_group: KeyGroup,
                 unassigned_post_group: KeyGroup,
                 ) -> None:
        self._color_groups: dict[KeyGroup, list[Key]] = collections.defaultdict(list)
        self._color_groups[unassigned_pre_group] = []
        for key_group, key_seq in color_groups.items():
            for key_name in key_seq:
                try:
                    self._color_groups[key_group].extend(self._iter_keys(key_name))
                except ValueError as error:
                    logger.warning("%s configures %s", key_group, error.args[0])
        assigned = frozenset(key for key_seq in self._color_groups.values() for key in key_seq)
        assigned_count = len(assigned)
        unassigned_count = len(KEY_ORDER) - assigned_count
        if unassigned_count:
            unassigned = [key for key in KEY_ORDER if key not in assigned]
            logger.warning(
                "configuration did not assign these keys,"
                " so they will be assigned to a new group: %s",
                ', '.join(repr(key) for key in unassigned),
            )
            if unassigned_count > assigned_count:
                unassigned_group = unassigned_pre_group
            else:
                unassigned_group = unassigned_post_group
            self._color_groups[unassigned_group] = unassigned
        if not self._color_groups[unassigned_pre_group]:
            del self._color_groups[unassigned_pre_group]
        self.group_count = len(self._color_groups)
        self._key_group_map = {
            key_name: group_name
            for group_name, group_keys in self._color_groups.items()
            for key_name in group_keys
        }

    @staticmethod
    def _iter_keys(name: str) -> Iterator[Key]:
        try:
            key_group = KeyAliases[name]
        except KeyError:
            if name in KEY_SET:
                yield name
            else:
                raise ValueError(f"unknown key {name!r}")
        else:
            yield from key_group.value

    @classmethod
    def from_config(cls, config: Mapping[str, Mapping[str, Any]]) -> 'KeyColorGroups':
        color_groups = {
            group_name: [
                key for key, value in group_config.items() if value is None
            ] for group_name, group_config in config.items()
        }
        if not any(color_groups.values()):
            logger.info("using default key groupings")
            color_groups = cls.DEFAULT_CONFIG
        post_group = max(color_groups)
        return cls(color_groups, '', post_group + post_group[-1])

    def led_lines(self, colors: Iterable[Color], *, fn: bool=False) -> Iterator[str]:
        color_map = dict(zip(self._color_groups, colors))
        if len(color_map) != self.group_count:
            raise ValueError(
                f"{self.group_count} colors provided, but need at least {len(color_map)}",
            )
        for key_name in KEY_ORDER:
            key_color = color_map[self._key_group_map[key_name]]
            yield key_color.freestyle_format(key_name, fn=fn)
