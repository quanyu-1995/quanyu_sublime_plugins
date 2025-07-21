import sublime
import sublime_plugin
import threading
import time
import codecs  # 添加codecs模块用于增量解码
import json

from .loading_animation import LoadingAnimation
from .get_connection import GetConnection

class QuanyuHttp(sublime_plugin.TextCommand):
	
    def run(self, edit):
        self.loading_animation = LoadingAnimation(self.view)
        self.loading_animation.start()

        threading.Thread(target=self.handle_request,).start()

    def handle_request(self):
        """后台线程执行网络请求"""
        conn = None
        # 获取选中区域内容
        region = self.view.sel()[0]
        config_str = self.view.substr(region)
        config = json.loads(config_str)

        point = region.a
        if region.b > region.a:
            point = region.b
        try:
            conn = GetConnection(self.view).get(config);
            # 获取响应
            response = conn.getresponse()
            status = response.status
            data = response.read().decode("utf-8")            
            res = 'status: \n{}\n\ndata:\n{}'.format(status, data)
            # 将结果调度回主线程
            sublime.set_timeout(lambda: self.append_result(res), 0)
        except Exception as e:
            str_e = str(e)
            sublime.set_timeout(lambda: self.append_result("请求失败: {}".format(str_e)), 0)
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    def append_result(self, res):
        """主线程更新UI"""
        self.loading_animation.stop()
        # 新开页签显示结果
        view = self.view.window().new_file()
        view.set_scratch(True)  # 设为临时文件，关闭时不提示保存
        # 插入结果
        view.run_command("insert_text_at_end", {"text": '{}\n'.format(res)})
