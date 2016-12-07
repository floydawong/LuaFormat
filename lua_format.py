
import sublime
import sublime_plugin
import sys, os

package_file = os.path.normpath(os.path.abspath(__file__))
lib_path = os.path.dirname(package_file)
lib_path = os.path.join(lib_path, "LuaFormat")
if lib_path not in sys.path:
    sys.path.append(lib_path)

import LuaFormat as lf


class LuaFormatCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # check lua file
        suffix_setting = self.view.settings().get('syntax')
        file_suffix = suffix_setting.split('.')[0]
        if file_suffix[-3:].lower() != 'lua': return

        # get content.
        region = sublime.Region(0, self.view.size())
        content = self.view.substr(region)
        
        # replace content
        self.view.replace(edit, region, lf.format(content))
