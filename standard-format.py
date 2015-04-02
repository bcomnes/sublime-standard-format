import sublime
import sublime_plugin
import subprocess
import os
import time
import merge_utils

# Please open issues if we are missing a common bin path
LOCAL = '/usr/local/bin:/usr/local/sbin'
os.environ['PATH'] = ":".join([LOCAL, os.environ['PATH']])

settings = None

# Thank you to the following ST plugins for providing a nice set of examples:
# - https://github.com/piuccio/sublime-esformatter
# - https://github.com/ionutvmi/sublime-jsfmt
# - https://github.com/enginespot/js-beautify-sublime
# - https://github.com/jdc0589/JsFormat/commits/master
# - https://github.com/akalongman/sublimetext-codeformatter
# - https://github.com/DisposaBoy/GoSublime


def plugin_loaded():
    global settings
    settings = sublime.load_settings("StandardFormat.sublime-settings")


def is_javascript(view):
    """Checks if the current view is javascript or not.  Used pre_save event"""
    # Check the file extension
    name = view.file_name()
    excludes = set(settings.get('excludes', []))
    includes = set(settings.get('includes', ['js']))
    if name and os.path.splitext(name)[1][1:] in includes - excludes:
        return True
    # If it has no name (?) or it's not a JS, check the syntax
    syntax = view.settings().get("syntax")
    if syntax and "javascript" in syntax.split("/")[-1].lower():
        return True
    return False


def standard_format(string):
    std = subprocess.Popen(
        ["standard-format"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    std.stdin.write(bytes(string, 'UTF-8'))
    out, err = std.communicate()
    return out.decode("utf-8"), err


class StandardFormatEventListener(sublime_plugin.EventListener):

    def on_pre_save(self, view):
        if settings.get("format_on_save") and is_javascript(view):
            view.run_command("standard_format")


class StandardFormatCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view
        regions = []
        sel = view.sel()

        for region in sel:
            if not region.empty():
                regions.append(region)

        if len(regions) < 1:
            # No selected regions, so format the whole file.
            allreg = sublime.Region(0, view.size())
            regions.append(allreg)

        for region in regions:
            self.do_format(edit, region, view)

        #self.format_whole_file(edit, opts, self.view)

    def do_format(self, edit, region, view):
        s = view.substr(region)
        s, err = standard_format(s)
        if not err and len(s) > 0:
            print('formatting')
            view.replace(edit, region, s)
        elif err:
            loud = settings.get("format_on_save")
            msg = 'standard-format: error formatting selection(s)'
            sublime.error_message(msg) if loud else sublime.status_message(msg)
