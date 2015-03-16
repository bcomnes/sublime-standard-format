# Standard Format
[WIP] Runs [standard-format](https://github.com/maxogden/standard-format) against the code in your ST3 window on save or manually.  Can be toggled on or off.  Besides that, there are no settings.

# WIP Instructions Dont work yet!

## Installation

Standard Format (the Sublime Plugin) requires that you install [`standard-format`]() to your global path:

```sh
$ npm install -g standard-format
```

Install Standard Format using [Package Control](https://packagecontrol.io/).

```sh
# In the command palate
- package control install
- standard format
```

## Configuration

You can find Standard Format settings in the `StandardFormat.sublime-settings` file.

- `format_on_save`: Boolean.  Runs Standard Format on save when set to true.
- `extensions`: String Array.  An array of file extensions that you want to be able to run Standard Format against.
- `standard-format-path`: String Path.  You don't have to set this.  Standard Format uses whichever `standard-format` is in your path.  This setting allows you to specify the path of which `standard-format` you are using.
