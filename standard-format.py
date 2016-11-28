import sublime
import sublime_plugin
import subprocess
import os
import shutil
# import inspect

SETTINGS_FILE = "StandardFormat.sublime-settings"
# Please open issues if we are missing a common bin path

# Initialize a global path.  Works on all OSs
global_path = os.environ["PATH"]
# load settings
settings = sublime.load_settings("StandardFormat.sublime-settings")
platform = sublime.platform()

def calculate_user_path(command=settings.get("get_path_command")):
    """execute a user shell to return a real env path"""
    return subprocess.check_output(command).decode("utf-8").replace('\n','')

def get_view_path(path_string):
    """
    walk the fs from the current view to find node_modules/.bin
    """
    view_path_array = []

    def search_for_bin_paths (path):

        dirname = path if os.path.isdir(path) else os.path.dirname(path)
        maybe_bin_path = os.path.join(dirname, 'node_modules', '.bin')
        found_path = os.path.isdir(maybe_bin_path)
        if found_path:
            view_path_array = view_path_array + [maybe_bin_path]
        if os.path.ismount(dirname):
            return
        else:
            search_for_bin_paths(os.path.dirname(dirname))

    search_for_bin_paths(path_string)
    return os.pathsep.join(project_path)

def get_project_path(view):
    """
    generate path of node_module/.bin for open project folders
    """
    parent_window_folders = view.window().folders()
    project_path = [get_view_path(folder) for folder in parent_window_folders]
    return os.pathsep.join(list(filter(None, project_path)))

def generate_search_path(view):
    """
    run necessary work to generate a search path
    """
    user_path = os.pathsep.join(settings.get("PATH"))
    search_path = [user_path]
    if settings.get("use_view_path"):
        if view.file_name():
            search_path = search_path + [get_view_path(view.file_name())]
        elif settings.get("use_view_path"):
            search_path = search_path + [get_project_path(view)]
    if settings.get("use_global_path"):
        search_path = search_path + [global_path]

    return os.pathsep.join(list(filter(None, search_path)))

def set_base_path(user_paths):
    # Please open issues if we are missing a common bin path
    """
    set up the correct path to search for one of the desired tools
    """
    path_array = well_known + user_paths
    paths = os.pathsep.join(path_array)
    os.environ["PATH"] = os.pathsep.join([paths, DEFAULT_PATH])
    msg = "StandardFormat Search Path: " + os.environ["PATH"]
    print(msg)

def get_command(commands):
    """
    Tries to validate and return a working formatting command
    """
    for command in commands:
        if shutil.which(command[0]):
            print("found {} at {}".format(command[0], shutil.which(command[0])))
            return command
    print("command not found")
    return None

def plugin_loaded():
    """
    perform some work to set up env correctly.
    """
    if settings.get("calculate_user_path") && platform == "windows":
        # Update global_path with calculated user path 
        global_path = calculate_user_path()
    view = sublime.active_window().active_view()
    search_path = generate_search_path(view)
    print(search_path)
    os.environ["PATH"] = search_path


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

    def on_activated_async(self, view):
        if is_javascript(view):
            search_path = generate_search_path(view)
            print(search_path)
            os.environ["PATH"] = search_path

class StandardFormatCommand(sublime_plugin.TextCommand):

    def run(self, edit, auto_save=None):
        # Figure out if the desired formatter is available
        command = get_command(settings.get("commands"))
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
