# config_utils.py
import sublime

class ConfigManager:
    """配置管理工具类"""
    _settings = None
    
    @classmethod
    def get_settings(cls):
        """获取插件设置"""
        if not cls._settings:
            # 加载或重新加载设置
            cls.reload_settings()
        return cls._settings
    
    @classmethod
    def reload_settings(cls):
        """重新加载设置"""
        cls._settings = sublime.load_settings("QuanyuChat.sublime-settings")
        
        # 添加设置更改监听器
        if not hasattr(cls, 'settings_listener'):
            cls.settings_listener = lambda: cls.reload_settings()
            cls._settings.add_on_change("quanyu-chat-settings", cls.settings_listener)
    
    @classmethod
    def get(cls, key, default=None):
        """获取配置项"""
        settings = cls.get_settings()
        return settings.get(key, default)
    
    @classmethod
    def set(cls, key, value):
        """设置配置项"""
        settings = cls.get_settings()
        settings.set(key, value)
        sublime.save_settings("QuanyuChat.sublime-settings")
    
    @classmethod
    def api_key(cls):
        """获取API密钥"""
        return cls.get("api_key", "")
    
    @classmethod
    def api_url(cls):
        """获取API URL"""
        return cls.get("api_url", "api.deepseek.com")
    
    @classmethod
    def api_endpoint(cls):
        """获取API端点"""
        return cls.get("api_endpoint", "/chat/completions")
    
    @classmethod
    def model(cls):
        """获取模型名称"""
        return cls.get("model", "deepseek-chat")
    
    @classmethod
    def conn_timeout(cls):
        """获取连接超时时间"""
        return cls.get("conn_timeout", 5.0)
    
    @classmethod
    def req_timeout(cls):
        """获取请求超时时间"""
        return cls.get("req_timeout", 60.0)