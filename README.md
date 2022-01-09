# Monkeypaint

## What Monkeypaint Does

Monkeypaint writes lighting profiles for the Kinesis Gaming Freestyle Edge RGB keyboard. You configure key groupings, and optionally a base color, and Monkeypaint will generate an entire color palette that you can save directly to the keyboard and load instantly.

## Why I Wrote Monkeypaint

![A clip from BoJack Horseman where Wanda exclaims over a tablet, "Ooh, cool! I love stupid bullshit like this!"](https://tv-memes.getyarn.io/yarn-clip/beec45e8-bc62-42cd-97b9-c2fd53d39fdb/gif)

More seriously: I like changing my keyboard's colors occasionally, but Kinesis' own software is tedious to use, and I have to boot to Windows to use it. Monkeypaint lets me change colors whenever I want with a quick command, and the results usually look nice. (Sometimes I get a bad combination of colors with my key groupings, but then I just run it again to get a different palette.)

## Credit Where Credit Is Due

The job of actually generating the color palette from a seed color is done by [The Color API][] by [Josh Beckman][]. Monkeypaint just reads your configuration to ask The Color API for a palette that meets your needs, and then writes it in the keyboard's profile format.

[The Color API]: https://www.thecolorapi.com/
[Josh Beckman]: https://www.joshbeckman.org/

## Installing Monkeypaint

Monkeypaint requires Python 3.9+ and a few Python modules. After you [install Python 3][], run:

      python3 -m pip install --user monkeypaint

[install Python 3]: https://wiki.python.org/moin/BeginnersGuide/Download

## Configuring Monkeypaint

1. Create the Monkeypaint configuration directory, if it doesn't already exist:

    Operating System | Monkeypaint Configuration Directory
    ---------------- | -----------------------------------------
    Linux            | `$HOME/.config/monkeypaint`
    macOS            | `$HOME/Library/Preferences/monkeypaint`
    Windows          | `%APP_DATA%/monkeypaint`

2. Copy [`config.ini`](config.ini) to that configuration directory.

3. Open the copy of `config.ini` in your configuration directory in your editor, and update it following the comments.

### Key Names

You define a group of keys by writing them as a list, one per line, all in one section of your configuration file. For example:

        [Group 1]
        esc
        f1
        w
        a
        s
        d
        …

For most keys, the name you use in configuration is the name that's printed on the keycap, without any spaces or capitalization (e.g., `prtsc`, `del`, `pgup`, `pgdn`). For keys with symbols on them, use the following names:

  Key Symbol          | Configuration name(s)
  ------------------- | ----------------------------------------
  Kinesis logo        | `hotkey0`, `hk0`
  ①                   | `hotkey1`, `hk1`
  ②                   | `hotkey2`, `hk2`
  ③                   | `hotkey3`, `hk3`
  ④                   | `hotkey4`, `hk4`
  ⑤                   | `hotkey5`, `hk5`
  ⑥                   | `hotkey6`, `hk6`
  ⑦                   | `hotkey7`, `hk7`
  ⑧                   | `hotkey8`, `hk8`
  ``` ~``             | `grave`, `tilde`
  `- _`               | `dash`, `hyphen`, `hyph`
  `= +`               | `equal`, `equals`, `eq`
  `[ {`               | `openbracket`, `openbrace`, `obracket`, `obrace`
  `] }`               | `closebracket`, `closebrace`, `cbracket`, `cbrace`
  `\ |`               | `backslash`, `bslash`
  `; :`               | `colon`
  `' "`               | `quote`, `apostrophe`, `apos`
  `, <`               | `comma`, `com`
  `. >`               | `dot`, `period`, `per`
  `/ ?`               | `forwardslash`, `fslash`
  ⛭                   | `backlight`, `light`, `led`
  Windows logo        | `windows`, `win`
  ↑                   | `up`, `uparrow`
  ←                   | `left`, `leftarrow`
  ↓                   | `down`, `downarrow`
  →                   | `right`, `rightarrow`

For keys on both sides of the keyboard (Ctrl, Alt, Shift, and Space), you can prefix the name with `left`/`l` and `right`/`r` to specify the one you want:

  Name for both keys | Name for left key | Name for right key
  ------------------ | ----------------- | ------------------
  `ctrl`             | `lctrl`           | `rctrl`
  `alt`              | `lalt`            | `ralt`
  `shift`            | `lshift`          | `rshift`
  `space`            | `lspace`          | `rspace`

For convenience, Monkeypaint recognizes names to address common sets of keys. You can write one of these set names in your configuration just like you would write a key name, and it includes all the keys in the key grouping:

  Set name(s)                           | Description
  ------------------------------------- | ------------------------------------
  `actions`, `action`, `act`            | Escape, Print Screen, Pause, and Windows logo
  `alphabet`, `alpha`                   | All the letters
  `digits`, `digit`                     | All the numbers
  `alphanumeric`, `alpha`               | All the letters and numbers
  `arrows`, `arrow`                     | All four navigation arrows
  `editing`, `edit`                     | Backspace, Delete, Enter, and Tab
  `function`, `func`                    | F1 through F12
  `hotkeys`, `hot`                      | The Kinesis Logo key and hotkeys ① through ⑧
  `meta`                                | Caps, Ctrl, Alt, and Shift (both sides)
  `navigation`, `nav`                   | Home, End, Page Up, and Page Down
  `punctuation`, `punc`                 | The keys ``` - = [ ] \ ; ' , . /``
  `row1`                                | The top row of keys, from the Kinesis logo key through Delete
  `row2`                                | The second row of keys, from hotkey ① through Home
  `row3`                                | The third row of keys, from hotkey ③ through End
  `row4`                                | The fourth row of keys, from hotkey ⑤ through Page Up
  `row5`                                | The fifth row of keys, from hotkey ⑦ through Page Down
  `row6`                                | The bottom row of keys, from Fn through Right Arrow →

The example [`config.ini`](config.ini) included with Monkeypaint includes a complete configuration that puts all the keys on the keyboard into four groups, mostly using set names.

## Running Monkeypaint

Just run `monkeypaint` on the command line. The command includes options to specify a starting color; select one collection of key groupings from your configuration file; use a different configuration file; and specify an output location. Run `monkeypaint --help` for details.

After you save a new lighting profile to the keyboard storage, you need to reload it by holding the Settings key (the upper right key with a ⚙ on it) and pressing the digit for the profile number you saved.

## What Monkeypaint Doesn't Do

Monkeypaint hasn't been tested with the Kinesis Gaming TKO, or any other keyboard. It might be straightforward to add support, but I'd need help from people who own those keyboards.

Monkeypaint hasn't been tested on any other operating system or distribution besides Debian. I've done my best to try to make sure it will work, but I can't promise anything. If you try it out, please let me know how it goes.

Monkeypaint doesn't provide a GUI yet. You have to run it from the command line for now.

Because The Color API is a REST API, Monkeypaint doesn't work offline. I looked for Python libraries that might do palette generation like The Color API, but didn't find any. If you know of one, please let me know.

Monkeypaint doesn't let you assign arbitrary colors to keys. It selects all of the colors starting from the base color.

## Monkeypaint is Free Software

Monkeypaint is copyright © 2021 by [Brett Smith](mailto:brettcsmith@brettcsmith.org). You can use, share, and modify the program under the terms of the included [GNU Affero General Public License version 3](LICENSE.txt).
