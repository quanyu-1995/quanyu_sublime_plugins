# insert_text_at_end.py
import sublime
import sublime_plugin

class InsertTextAtEndCommand(sublime_plugin.TextCommand):
    """安全插入文本到文档末尾的命令"""
    def run(self, edit, text):
        try:
            # 在文档末尾插入文本
            self.view.insert(edit, self.view.size(), text)
            # 滚动到新内容
            self.view.show(self.view.size())
        except Exception as e:
            sublime.status_message("插入失败: {}".format(str(e)))