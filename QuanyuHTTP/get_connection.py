# get_connection.py
import sublime
import sublime_plugin
import http.client
import json

# from .config_utils import ConfigManager  # 导入配置管理工具
# from .build_messages import BuildMessages

class GetConnection(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.conn_timeout = 10
        self.req_timeout = 30

    def get(self, config):
        # 创建连接
        conn = http.client.HTTPSConnection(config["host"])
        conn.connect()
        conn.sock.settimeout(self.conn_timeout)
        
        # 发送请求
        if config["type"]=='POST':
            conn.request(config["type"], config["endpoint"], body=json.dumps(config["body"]), headers=config["headers"])
        elif config["type"]=='GET':
            query_parts = []
            for key, value in config["params"].items():
                query_parts.append("{}={}".format(key,value))
            query_str = '&'.join(query_parts)
            if '?' in config["endpoint"]:
                # 已有参数，用&连接
                separator = '&'
            else:
                # 没有参数，用?开始
                separator = '?'            
            full_url = "{}{}{}".format(config["endpoint"], separator, query_str)
            conn.request(config["type"], full_url, headers=config["headers"])
        # 设置读取超时
        conn.sock.settimeout(self.req_timeout)
        return conn