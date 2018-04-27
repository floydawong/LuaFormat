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

        # get lines of replacement
        r = sublime.Region(0, self.view.size())
        self.view.unfold(r)
        
        # get characters of view
        lines = []
        for region in self.view.lines(r):
            cache = self.view.substr(region)
            if len(cache) == 0: cache = ' '
            lines.append(cache)

        # get cursor position before the replacement
        selection = self.view.sel()[0].b
        row, col = self.view.rowcol(selection)

        # replace the content after format
        print("Run Lua Format")
        self.view.replace(edit, r, lua_format(lines, get_settings()))

        # set tab_size from lua-format-setting
        self.view.run_command("set_setting", {"setting": "tab_size", "value": get_settings().get('tab_size', 4)})

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
