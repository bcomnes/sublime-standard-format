# Standard Format
[![Build Status](https://travis-ci.org/bcomnes/sublime-standard-format.svg?branch=master)](https://travis-ci.org/bcomnes/sublime-standard-format)

A Sublime Text 3 plug-in that runs [standard-format](https://github.com/maxogden/standard-format) against the javascript code in your ST3 window on save or manually.  Can be toggled on or off.  Besides compatibility details, there are no settings.

![action gif](https://cdn.rawgit.com/bcomnes/sublime-standard-format/master/format.gif)

## Installation

Standard Format (the Sublime Text Plug-in) requires that you install [`standard-format`](https://github.com/maxogden/standard-format) to your global path:

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

- `format_on_save`: Boolean.  Runs Standard Format on save when set to true.  Use the command pallet to quickly toggle this on or off.
- `extensions`: String Array.  An array of file extensions that you want to be able to run Standard Format against.
- `excludes`: String Array.  An array of file extensions that you don't want to run against.
- `command`: String Array.  Customize the command and flags that **Standard Format** runs against.
- `PATH` **Not Implemented Yet**: String Array.  An Array of paths to be appended to the search PATH.
- `loud_error`: Boolean.  Specifies if you get a status bar message or error window if the subprocess encounters an error while formatting.

## Hints

**Standard Format** will try to find and use (`command` to format with if set, otherwise it will fall back to) `standard-format` or `standard`.

Windows support is coming very soon, but PRs welcome.

## Linter

Standard Format pairs nicely with the Sublime Text `standard` linter:

- [Flet/SublimeLinter-contrib-standard](https://github.com/Flet/SublimeLinter-contrib-standard)

## References

- https://github.com/piuccio/sublime-esformatter
- https://github.com/ionutvmi/sublime-jsfmt
- https://github.com/enginespot/js-beautify-sublime
- https://github.com/jdc0589/JsFormat/commits/master
- https://github.com/akalongman/sublimetext-codeformatter
- https://github.com/DisposaBoy/GoSublime
- https://github.com/Flet/SublimeLinter-contrib-standard

