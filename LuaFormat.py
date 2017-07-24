import sublime
import sublime_plugin
import sys
import os

if sublime.version().startswith('3'):
    from .core import *
else:
    from core import *


# ----------------------------------------------------------
# Setting
# ----------------------------------------------------------
def get_package_settings():
    setting_name = 'Default.sublime-settings'
    settings = sublime.load_settings(setting_name)
    return settings


def get_settings_param(view, param_name, default=None):
    settings = get_package_settings()
    project_settings = view.settings()
    return project_settings.get(param_name, settings.get(param_name, default))


# ----------------------------------------------------------
# Command
# ----------------------------------------------------------
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

        # load package settings
        settings = get_package_settings()
        tab_size = settings.get('tab_size', 4)
        separator_exclude = settings.get('separator_exclude', True)
        operator_exclude = settings.get('operator_exclude', True)
        bracket_exclude = settings.get('bracket_exclude', False)

        # replace the content after format
        self.view.replace(edit, region,
                          lua_format(
                              content,
                              tab_size=tab_size,
                              separator_exclude=separator_exclude,
                              operator_exclude=operator_exclude,
                              bracket_exclude=bracket_exclude))

        # deal cursor position
        selection = self.view.full_line(self.view.text_point(row - 1, 0)).b
        cursor_pos = sublime.Region(selection, selection)
        regions = self.view.sel()
        regions.clear()
        regions.add(cursor_pos)
        sublime.set_timeout_async(lambda: self.view.show_at_center(cursor_pos),
                                  0)


class LuaFormatOnPreSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        settings = get_package_settings()
        if settings.get('auto_format_on_save', False):
            view.run_command("lua_format")
