import sublime
import sublime_plugin
import subprocess
import os
import shutil

SETTINGS_FILE = "StandardFormat.sublime-settings"
LOCAL = ":".join(["/usr/local/bin", "/usr/local/sbin"])
os.environ["PATH"] = ":".join([LOCAL, os.environ["PATH"]])
# Please open issues if we are missing a common bin path

settings = None
command = None


def validate_command(command):
    """
    Tries to validate and return a working formatting command
    """
    if shutil.which(command[0]):
        # Try to use provided command
        return command
    elif command[0] != "standard-format" and shutil.which("standard-format"):
        # Otherwise just use standard-format
        msg = "{} could not be found. Using standard-format".format(
            command[0])
        print("StandardFormat: " + msg)
        return ["standard-format", "--stdin"]
    elif shutil.which("standard"):
        # and if that isn't around use standard
        msg = "Can't find standard-format.  Falling back to standard"
        print("StandardFormat: " + msg)
        return ["standard", "--format", "--stdin"]
    else:
        msg = "Please install standard-format: 'npm i standard-format -g' \
            or extend PATH in settings"
        print("StandardFormat: " + msg)
        return None


def plugin_loaded():
    global settings
    global command
    settings = sublime.load_settings("StandardFormat.sublime-settings")
    command = validate_command(settings.get("command"))


def is_javascript(view):
    """
    Checks if the current view is javascript or not.  Used in pre_save event.
    """
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


def standard_format(string, command):
    """
    Uses subprocess to format a given string.
    """
    std = subprocess.Popen(
        command,
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
        if not command:
            # Noop if we don't have the right tools.
            return None
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

    def do_format(self, edit, region, view):
        s = view.substr(region)
        s, err = standard_format(s, command)
        if not err and len(s) > 0:
            view.replace(edit, region, s)
        elif err:
            loud = settings.get("format_on_save")
            msg = 'standard-format: error formatting selection(s)'
            sublime.error_message(msg) if loud else sublime.status_message(msg)


class ToggleStandardFormatCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        if settings.get('format_on_save', False):
            settings.set('format_on_save', False)
            sublime.status_message("Format on save: Off")
        else:
            settings.set('format_on_save', True)
            sublime.status_message("Format on save: On")
        sublime.save_settings(SETTINGS_FILE)

    def is_checked(self):
        return settings.get('format_on_save', False)
