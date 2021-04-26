import sublime
import sublime_plugin
import subprocess
import os
import re
import shutil
# import inspect

PLUGIN_NAME = "StandardFormat"
SETTINGS_FILE = "{}.sublime-settings".format(PLUGIN_NAME)
PROJECT_SETTINGS_KEY = "standard_format"

# load settings
settings = None
platform = sublime.platform()
global_path = os.environ["PATH"]
local_path = ""
package_root_path = ""
selectors = {}

SYNTAX_RE = re.compile(r'(?i)/([^/]+)\.(?:tmLanguage|sublime-syntax)$')


def calculate_env():
    """Generate environment based on global environment and local path"""
    global local_path
    env = dict(os.environ)
    env["PATH"] = local_path
    return env


# Initialize a global path.  Works on Unix only only right now
def calculate_user_path(view):
    """execute a user shell to return a real env path"""
    shell_command = get_setting("get_path_command")
    user_path = (
        subprocess.check_output(shell_command)
        .decode("utf-8")
        .split('\n')
    )
    maybe_path = [string for string in user_path
                  if len(string) > 0 and string[0] == os.sep]
    return maybe_path


def get_package_root(path, top=""):
    """
    Return the path of the nearest package.json, otherwise just the directory
    of the view.
    """
    dirname = path if os.path.isdir(path) else os.path.dirname(path)
    maybe_package_root = os.path.join(dirname, 'package.json')
    is_package_root = os.path.isfile(maybe_package_root)

    return (
        dirname if is_package_root
        else top if os.path.ismount(dirname)
        else get_package_root(os.path.dirname(dirname), top or dirname)
    )


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
    try:
        parent_window_folders = view.window().folders()
    except Exception:
        parent_window_folders = []
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
    search_path = get_setting("PATH")
    if not isinstance(search_path, list):
        print(
            "StandardFormat: PATH in settings does not appear to be an array")
        search_path = []
    if get_setting("use_view_path"):
        if view.file_name():
            search_path = search_path + [get_view_path(view.file_name())]
        elif get_setting("use_project_path_fallback"):
            search_path = search_path + [get_project_path(view)]
    if get_setting("use_global_path"):
        search_path = search_path + [global_path]
    search_path = list(filter(None, search_path))
    new_path = os.pathsep.join(search_path)
    return new_path


def get_command(commands):
    """
    Tries to validate and return a working formatting command
    """
    for command in commands:
        if shutil.which(command[0], path=local_path):
            return command
    return None


def print_status(view, global_path, search_path, root_path):
    command = get_command(get_setting("commands"))
    print("StandardFormat:")
    print("  global_path: {}".format(global_path))
    print("  search_path: {}".format(search_path))
    print("  root_path: {}".format(root_path))
    if command:
        print("  found {} at {}".format(
            command[0], shutil.which(command[0], path=local_path)))
        print("  command: {}".format(command))
        if get_setting("check_version"):
            print(
                "  {} version: {}"
                .format(command[0], command_version(
                    shutil.which(command[0], path=local_path)))
             )


def get_setting(key, default_value=None):
    project_value = _get_project_setting(key)
    if project_value is None:
        return settings.get(key, default_value)
    return project_value


def _get_project_setting(key):
    view = sublime.active_window().active_view()
    project_settings = view.settings()
    if not project_settings:
        return None
    sub_settings = project_settings.get(PROJECT_SETTINGS_KEY)
    if sub_settings and key in sub_settings:
        return sub_settings[key]
    return None


def plugin_loaded():
    """
    perform some work to set up env correctly.
    """
    global global_path
    global local_path
    global package_root_path
    global settings
    settings = sublime.load_settings(SETTINGS_FILE)
    view = sublime.active_window().active_view()
    if platform != "windows":
        maybe_path = calculate_user_path(view)
        if len(maybe_path) > 0:
            global_path = maybe_path[0]
    search_path = generate_search_path(view)
    local_path = search_path
    package_root_path = get_package_root(view.file_name())
    print_status(view, global_path, search_path, package_root_path)


class StandardFormatEventListener(sublime_plugin.EventListener):

    def on_pre_save(self, view):
        global package_root_path
        if get_setting("format_on_save") and is_javascript(view):
            os.chdir(package_root_path or os.path.dirname(view.file_name()))
            view.run_command("standard_format")

    def on_activated_async(self, view):
        global local_path
        global package_root_path
        search_path = generate_search_path(view)
        local_path = search_path
        if is_javascript(view):
            package_root_path = get_package_root(view.file_name())
        if is_javascript(view) and get_setting("logging_on_view_change"):
            print_status(view, global_path, search_path, package_root_path)


def is_javascript(view):
    """
    Checks if the current view is JS or not.  Used in pre_save event.
    """
    # Check the file extension
    name = view.file_name()
    extensions = set(get_setting('extensions'))
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
        env=calculate_env(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        startupinfo=startupinfo
    )

    std.stdin.write(bytes(string, 'UTF-8'))
    out, err = std.communicate()
    retcode = std.returncode
    print(err)
    return out.decode("utf-8"), err, retcode


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
        env=calculate_env(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        startupinfo=startupinfo
    )
    out, err = std.communicate()
    return out.decode("utf-8").replace("\r", ""), err


class StandardFormatCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        global package_root_path
        view = self.view

        # Figure out if the desired formatter is available
        command = get_command(get_setting("commands"))

        if platform == "windows" and command is not None:
            # Windows hax
            command[0] = shutil.which(command[0], path=local_path)
        if not command:
            # Noop if we don't have the right tools.
            return None

        view_syntax = view.settings().get('syntax', '')

        if view_syntax:
            match = SYNTAX_RE.search(view_syntax)

            if match:
                view_syntax = match.group(1).lower()
            else:
                view_syntax = ''

        if view_syntax and view_syntax in get_setting('extensions', []):
            selectors = get_setting("selectors")
            selector = selectors[view_syntax]
        else:
            selector = None

        os.chdir(package_root_path or os.path.dirname(view.file_name()))

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
        s, err, retcode = standard_format(s, command)
        if len(s) > 0:
            view.replace(edit, region, s)
        elif err:
            loud = get_setting("loud_error")
            msg = 'standard-format error: %s' % err.decode('utf-8').strip()
            print(msg)
            if get_setting("log_errors"):
                print(err)
            sublime.error_message(msg) if loud else sublime.status_message(msg)


class ToggleStandardFormatCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        if get_setting('format_on_save', False):
            settings.set('format_on_save', False)
            sublime.status_message("Format on save: Off")
        else:
            settings.set('format_on_save', True)
            sublime.status_message("Format on save: On")
        sublime.save_settings(SETTINGS_FILE)

    def is_checked(self):
        return get_setting('format_on_save', False)
