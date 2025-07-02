# quanyu_chat_reload_settings.py
import sublime
import sublime_plugin

class QuanyuChatReloadSettingsCommand(sublime_plugin.ApplicationCommand):
    """重载插件设置"""
    def run(self):
        from .config_utils import ConfigManager
        ConfigManager.reload_settings()
        sublime.status_message("Quanyu Chat 设置已重新加载")