import sublime
import sublime_plugin
import sys


def reload(name):
    rubbish_pool = []
    for key in sys.modules:
        if name in key:
            rubbish_pool.append(key)
    for key in rubbish_pool:
        del sys.modules[key]


reload('LuaFormat.core')

if sublime.version().startswith('3'):
    from .core import *
else:
    from core import *


def get_settings():
    return sublime.load_settings('LuaFormat.sublime-settings')


class LuaFormatCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # check whether the lua files
        suffix_setting = self.view.settings().get('syntax')
        file_suffix = suffix_setting.split('.')[0]
        if file_suffix[-3:].lower() != 'lua': return

        # get content of replacement
        region = sublime.Region(0, self.view.size())
        content = self.view.substr(region)

        # get cursor position before the replacement
        selection = self.view.sel()[0].b
        row, col = self.view.rowcol(selection)

        # replace the content after format
        self.view.replace(edit, region, lua_format(content, get_settings()))

        # deal cursor position
        selection = self.view.full_line(self.view.text_point(row - 1, 0)).b
        cursor_pos = sublime.Region(selection, selection)
        regions = self.view.sel()
        regions.clear()
        regions.add(cursor_pos)
        sublime.set_timeout_async(lambda: self.view.show(cursor_pos), 0)


class LuaFormatOnPreSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        if get_settings().get('auto_format_on_save', False):
            view.run_command("lua_format")
