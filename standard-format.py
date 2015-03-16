import sublime
import sublime_plugin
import subprocess
import os

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


class StandardFormatEventListener(sublime_plugin.EventListener):

    def on_pre_save(self, view):
        if self.is_javascript(view):
            print('standard format just did something')

    def is_javascript(self, view):
        """ Checks if the file being worked on is JS"""
        # Check the file extension
        name = view.file_name()
        if name and os.path.splitext(name)[1][1:] in ["js"]:
            return True
        # If it has no name (?) or it's not a JS, check the syntax
        syntax = view.settings().get("syntax")
        if syntax and "javascript" in syntax.split("/")[-1].lower():
            return True

        return False
