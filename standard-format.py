import sublime
import sublime_plugin
import subprocess
import os
import re
import shutil
# import inspect

SETTINGS_FILE = "StandardFormat.sublime-settings"

# load settings
settings = None
platform = sublime.platform()
global_path = os.environ["PATH"]
selectors = {}

SYNTAX_RE = re.compile(r'(?i)/([^/]+)\.(?:tmLanguage|sublime-syntax)$')

# Initialize a global path.  Works on all OSs


def calculate_user_path():
    """execute a user shell to return a real env path"""
    shell_command = settings.get("get_path_command")
    user_path = (
        subprocess.check_output(shell_command)
        .decode("utf-8")
        .split('\n')[0]
    )
    return user_path


def search_for_bin_paths(path, view_path_array=[]):
    dirname = path if os.path.isdir(path) else os.path.dirname(path)
    maybe_bin_path = os.path.join(dirname, 'node_modules', '.bin')
    found_path = os.path.isdir(maybe_bin_path)
    if found_path:
        view_path_array = view_path_array + [maybe_bin_path]
    return (
        view_path_array if os.path.ismount(dirname)
        else search_for_bin_paths(os.path.dirname(dirname), view_path_array)
    )


def get_view_path(path_string):
    """
    walk the fs from the current view to find node_modules/.bin
    """
    project_path = search_for_bin_paths(path_string)
    return os.pathsep.join(project_path)


def get_project_path(view):
    """
    generate path of node_module/.bin for open project folders
    """
    parent_window_folders = view.window().folders()
    project_path = (
        [get_view_path(folder) for folder in parent_window_folders] if
        parent_window_folders
        else []
    )
    return os.pathsep.join(list(filter(None, project_path)))


def generate_search_path(view):
    """
    run necessary work to generate a search path
    """
    search_path = settings.get("PATH")
    if not isinstance(search_path, list):
        print("StandardFormat: PATH in settings does not appear to be an array")
        search_path = []
    if settings.get("use_view_path"):
        if view.file_name():
            search_path = search_path + [get_view_path(view.file_name())]
        elif settings.get("use_project_path_fallback"):
            search_path = search_path + [get_project_path(view)]
    if settings.get("use_global_path"):
        search_path = search_path + [global_path]
    search_path = list(filter(None, search_path))
    new_path = os.pathsep.join(search_path)

    return new_path


def get_command(commands):
    """
    Tries to validate and return a working formatting command
    """
    for command in commands:
        if shutil.which(command[0]):
            return command
    return None


def print_status(global_path, search_path):
    command = get_command(settings.get("commands"))
    print("StandardFormat:")
    print("  global_path: {}".format(global_path))
    print("  search_path: {}".format(search_path))
    if command:
        print("  found {} at {}".format(command[0], shutil.which(command[0])))
        print("  command: {}".format(command))
        if settings.get("check_version"):
            print(
                "  {} version: {}"
                .format(command[0], command_version(command[0]))
            )


def plugin_loaded():
    """
    perform some work to set up env correctly.
    """
    global global_path
    global settings
    settings = sublime.load_settings(SETTINGS_FILE)
    view = sublime.active_window().active_view()
    if platform != "windows":
        global_path = calculate_user_path()
    search_path = generate_search_path(view)
    os.environ["PATH"] = search_path
    print_status(global_path, search_path)


class StandardFormatEventListener(sublime_plugin.EventListener):

    def on_pre_save(self, view):
        if settings.get("format_on_save") and is_javascript(view):
            os.chdir(os.path.dirname(view.file_name()))
            view.run_command("standard_format")

    def on_activated_async(self, view):
        search_path = generate_search_path(view)
        os.environ["PATH"] = search_path
        if is_javascript(view) and settings.get("logging_on_view_change"):
            print_status(global_path, search_path)


def is_javascript(view):
    """
    Checks if the current view is JS or not.  Used in pre_save event.
    """
    # Check the file extension
    name = view.file_name()
    extensions = set(settings.get('extensions'))
    if name and os.path.splitext(name)[1][1:] in extensions:
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

    startupinfo = None

    if platform == "windows":
        # Prevent cmd.exe window from popping up
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= (
            subprocess.STARTF_USESTDHANDLES | subprocess.STARTF_USESHOWWINDOW
        )
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
    print(err)
    return out.decode("utf-8"), None


def command_version(command):
    """
    Uses subprocess to format a given string.
    """

    startupinfo = None

    if platform == "windows":
        # Prevent cmd.exe window from popping up
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= (
            subprocess.STARTF_USESTDHANDLES | subprocess.STARTF_USESHOWWINDOW
        )
        startupinfo.wShowWindow = subprocess.SW_HIDE

    std = subprocess.Popen(
        [command, "--version"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        startupinfo=startupinfo
    )
    out, err = std.communicate()
    return out.decode("utf-8").replace("\r", ""), err


class StandardFormatCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        # Figure out if the desired formatter is available
        command = get_command(settings.get("commands"))
        if platform == "windows" and command is not None:
            # Windows hax
            command[0] = shutil.which(command[0])
        if not command:
            # Noop if we don't have the right tools.
            return None
        view = self.view

        view_syntax = view.settings().get('syntax', '')

        if view_syntax:
            match = SYNTAX_RE.search(view_syntax)

            if match:
                view_syntax = match.group(1).lower()
            else:
                view_syntax = ''

        if view_syntax and view_syntax in settings.get('extensions', []):
            selectors = settings.get("selectors")
            selector = selectors[view_syntax]
        else:
            selector = None

        os.chdir(os.path.dirname(view.file_name()))

        regions = []
        # sel = view.sel()

        if selector:
            regions = view.find_by_selector(selector)
        else:
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
            if settings.get("log_errors"):
                print(err)
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
