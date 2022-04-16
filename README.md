# Standard Format

Sublime Text package to provide formatting with [standardjs](https://standardjs.com/). Matching `.js`, `.jsx`, `.ts`, and `.tsx`, source files.

## Requirements

1. Standard JS is a requirement, please follow the installation instructions [here](https://standardjs.com/index.html#install).
2. TypeScript is optional/available, please follow the installation instructions [here](https://standardjs.com/#typescript).

## Install

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) to open the Command Palette
2. Select **Package Control: Install Package**
3. Select **StandardFormat**

## Linter Integration

Standard Format pairs nicely with the following [SublimeLinter](https://www.sublimelinter.com/en/latest/) plugins:

- [SublimeLinter-contrib-standard](https://packagecontrol.io/packages/SublimeLinter-contrib-standard)
- [SublimeLinter-contrib-semistandard](https://packagecontrol.io/packages/SublimeLinter-contrib-semistandard)
- [SublimeLinter-contrib-ts-standard](https://packagecontrol.io/packages/SublimeLinter-contrib-ts-standard)

## Usage

When `format_on_save` is enabled, the plugin runs the following commands against the matching source files:

```json
{
  "commands": [
    ["standard", "--stdin", "--fix"],
    ["semistandard", "--stdin", "--fix" ]
    ["ts-standard", "--stdin", "--fix", "--stdin-filename", "{FILENAME}" ]
  ]
}
```

## Configuration

Standard Format is agressive about finding your developer dependencies.  The search path that it uses by default are in the following order:

- User added paths: you can add an array of paths in your settings file.  You shouldn't need to do this unless you are doing something weird.
- Any `node_modules/.bin` paths found above the current file.  Disable with `use_view_path`
- If your current view isn't saved to disk, any any folders in the project will be walked towards root searching for `node_modules/.bin` to add to the path here.  Disabled with `use_project_path_fallback`.
- The global user path is then used if nothing else is found.  This is calculated by starting a bash instance and calculating the real user path, including `.nvm` shims.

### Other settings:

- `format_on_save`: Boolean.  Runs Standard Format on save when set to true.  Use the command pallet to quickly toggle this on or off.
- `extensions`: String Array.  An array of file extensions that you want to be able to run Standard Format against.
- `command`: **Optional** String Array.  Customize the command and flags that **Standard Format** runs against. Can expand certain pre-defined placeholders (such as `{FILENAME}`).
- `loud_error`: Boolean. Specifies if you get a status bar message or error window if the subprocess encounters an error while formatting.
- `log_errors`: Boolean. Lets you log out errors encountered by the formatter.  Mainly used to suppress noisy formatting errors.

## Contributing

Contributions are more than welcome :) Should you like to help out, please bear in mind that contribution should follow the guidelines specified in the [pyproject.toml](./pyproject.toml) file. (**flake8**, **black**).
