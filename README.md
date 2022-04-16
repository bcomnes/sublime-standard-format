# Standard Format

Sublime Text integration with [standardjs](https://standardjs.com/). Matching JavaScript, JSX, TypeScript, and TSX, source files.

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

This package offers minimal and sane defaults to format the currently open file on save. For anything sophisticated, it's advisable to rely on your `package.json`

## Configuration

Use **either** `standard` **or** `semistandard` for `.jx` and `.jsx`, and optionally `ts-standard` for `.ts` and `.tsx`.

Should you want to disable `format_on_save` for some reason, you can set it to `false` in the settings.

This package will use your operating system `$PATH` environment variable. Should you need anything different, you can set `path` too.

```json
{
    "standard_format": "standard",
    "enable_typescript": false,
    "format_on_save": true,
    "path": [],
}
```

## Contributing

Contributions are more than welcome :) Should you like to help out, please bear in mind that contribution should follow the guidelines specified in the [pyproject.toml](./pyproject.toml) file. (**flake8**, **black**).
