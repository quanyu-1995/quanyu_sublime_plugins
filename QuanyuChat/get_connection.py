# get_connection.py
import sublime
import sublime_plugin
import http.client
import json

from .config_utils import ConfigManager  # 导入配置管理工具
from .build_messages import BuildMessages

class GetConnection(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.api_key = ConfigManager.api_key()
        self.api_url = ConfigManager.api_url()
        self.api_endpoint = ConfigManager.api_endpoint()
        self.model = ConfigManager.model()
        self.conn_timeout = ConfigManager.conn_timeout()
        self.req_timeout = ConfigManager.req_timeout()
        self.messages = BuildMessages(view).get()

    def get(self, stream):
        # 准备请求数据
        data = {
            "model": self.model,
            "messages": self.messages,
            "stream": stream  # 启用流式
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key
        }
        # 创建连接
        sublime.status_message("创建连接")
        conn = http.client.HTTPSConnection(self.api_url)
        conn.connect()
        conn.sock.settimeout(self.conn_timeout)
        
        # 发送请求
        sublime.status_message("发送请求")
        conn.request("POST", self.api_endpoint, body=json.dumps(data), headers=headers)
        
        # 设置读取超时
        conn.sock.settimeout(self.req_timeout)
        
        # 获取响应
        return conn