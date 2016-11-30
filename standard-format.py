import sublime
import sublime_plugin
import subprocess
import os
import shutil

SETTINGS_FILE = "StandardFormat.sublime-settings"
# Please open issues if we are missing a common bin path

DEFAULT_PATH = os.environ["PATH"]
settings = None
platform = sublime.platform()

# List of known "false positive" syntax files
JAVASCRIPT_SYNTAX_BLACKLIST = [
    'JSON (JavaScriptNext).tmLanguage'
]


def set_path(user_paths):
    # Please open issues if we are missing a common bin path
    well_known = [os.path.join('.', 'node_modules', '.bin'),
                  os.path.join(os.path.expanduser('~'), 'npm-global', 'bin'), '/usr/local/bin']
    path_array = user_paths + well_known
    paths = os.pathsep.join(path_array)
    os.environ["PATH"] = os.pathsep.join([paths, DEFAULT_PATH])
    msg = "Standard Format Search Path: " + os.environ["PATH"]
    print(msg)


def get_command(command):
    """
    Tries to validate and return a working formatting command
    """
    if shutil.which(command[0]):
        # Try to use provided command
        return command
    elif command[0] != "standard" and shutil.which("standard"):
        # Otherwise just use standard
        msg = "{} could not be found. Using standard".format(
            command[0])
        print("StandardFormat: " + msg)
        return ["standard", "--stdin", "--fix"]
    else:
        msg = "Please install standard: 'npm i standard -g' \
            or extend PATH in settings"
        print("StandardFormat: " + msg)
        return None


def plugin_loaded():
    global settings
    settings = sublime.load_settings("StandardFormat.sublime-settings")

    # Add custom user paths
    user_paths = settings.get("PATH")
    set_path(user_paths)


def is_javascript(view):
    """
    Checks if the current view is javascript or not.  Used in pre_save event.
    """
    # Check the file extension
    name = view.file_name()
    excludes = set(settings.get('excludes', []))
    includes = set(settings.get('includes', ['js']))

    # Ignore files with no name
    # (When does this happen exactly?)
    if not name:
        return False

    # Check the extension against excluded and included extensions
    extension = os.path.splitext(name)[1][1:]
    if extension in excludes:
        return False
    if extension in includes:
        return True

    # The extension is unknown, so check the syntax
    syntax = view.settings().get("syntax")
    if not syntax:
        return False

    # Get the last part of the .tmLanguage path and filter using blacklist
    syntax = syntax.split("/")[-1]
    if syntax in JAVASCRIPT_SYNTAX_BLACKLIST:
        return False

    # If it looks like it's JavaScript, process it
    if 'javascript' in syntax.lower():
        return True

    return False


def standard_format(string, command):
    """
    Uses subprocess to format a given string.
    """

    startupinfo = None

    if platform == "windows":
        # Prevent cmd.exe window from popping up
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESTDHANDLES | subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    std = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        startupinfo=startupinfo
    )
    std.stdin.write(bytes(string, 'UTF-8'))
    out, err = std.communicate()
    return out.decode("utf-8").replace("\r", ""), err


class StandardFormatEventListener(sublime_plugin.EventListener):

    def on_pre_save(self, view):
        if settings.get("format_on_save") and is_javascript(view):
            view.run_command("standard_format", {"auto_save": True})


class StandardFormatCommand(sublime_plugin.TextCommand):

    def run(self, edit, auto_save=None):
        # Figure out if the desired formatter is available
        command = get_command(settings.get("command"))
        if platform == "windows" and command is not None:
            # Windows hax
            command[0] = shutil.which(command[0])
        if not command:
            # Noop if we don't have the right tools.
            return None
        view = self.view
        regions = []
        sel = view.sel()

        if auto_save:
            allreg = sublime.Region(0, view.size())
            regions.append(allreg)
        else:
            for region in sel:
                if not region.empty():
                    regions.append(region)

            if len(regions) < 1:
                # No selected regions, so format the whole file.
                allreg = sublime.Region(0, view.size())
                regions.append(allreg)

        for region in regions:
            self.do_format(edit, region, view, command)

    def do_format(self, edit, region, view, command):
        s = view.substr(region)
        s, err = standard_format(s, command)
        if not err and len(s) > 0:
            view.replace(edit, region, s)
        elif err:
            loud = settings.get("loud_error")
            msg = 'StandardFormat: error formatting selection(s)'
            print(msg)
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
