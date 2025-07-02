# replace_content.py
import sublime
import sublime_plugin

class ReplaceContentCommand(sublime_plugin.TextCommand):
    """替换视图全部内容"""
    def run(self, edit, content):
        # 清除所有内容
        region = sublime.Region(0, self.view.size())
        self.view.replace(edit, region, content)