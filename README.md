# GotoLastEdit

A Sublime Text plugin that jumps to previous edit locations — including edits in other tabs.

## Install

### Manual

1. Open the Sublime Text Packages folder
   (`Preferences → Browse Packages…`).
2. Clone or copy this folder there as `GotoLastEdit`:

```bash
cd "$(python3 -c 'import os; print(os.path.expanduser("~"))')"  # then open Packages via the menu
git clone <this-repo-url> GotoLastEdit
```

3. Restart Sublime Text (or wait for the plugin to reload).

### From the original Package Control package

If you already have the Package Control package installed, replace its files with the ones from this repo (or remove it and use the manual install above) so you pick up these fixes.

## Usage

Default binding (all platforms):

```
Ctrl + Q
```

Each press walks further back through recent edit locations. When the most recent edit was in another tab, the command focuses that tab and selects the edited line.

### Key binding conflicts

On some Linux builds and Sublime Text 3/4 setups, `Ctrl+Q` is also bound to quit. Remap via
`Preferences → Package Settings → GotoLastEdit → Key Bindings`, for example:

```json
[
    {
        "keys": ["ctrl+alt+q"],
        "command": "last_edit_line"
    }
]
```

The command name is `last_edit_line`.

## Settings

`Preferences → Package Settings → GotoLastEdit → Settings`:

```json
{
    "history_size": 50
}
```

Increase `history_size` to keep more edit locations (both per buffer and across views).

## Development / tests

These tests run without Sublime Text, using lightweight API stubs:

```bash
python3 -m unittest discover -s tests -v
```

## License

Free to use and modify