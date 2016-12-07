
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
        # Check whether the Lua files
        suffix_setting = self.view.settings().get('syntax')
        file_suffix = suffix_setting.split('.')[0]
        if file_suffix[-3:].lower() != 'lua': return

        # Get content of replacement
        region = sublime.Region(0, self.view.size())
        content = self.view.substr(region)
        print(len(content))

        # Get cursor position before the replacement
        tp = self.view.sel()[0].b
        row, col = self.view.rowcol(tp)

        self.view.replace(edit, region, lf.format(content))

        # Deal cursor position
        ntp = self.view.line(self.view.text_point(row, 0)).b
        regions = self.view.sel()
        regions.clear()
        regions.add(sublime.Region(ntp, ntp))
        sublime.set_timeout_async(lambda: self.view.show_at_center(sublime.Region(ntp, ntp)), 20)
        