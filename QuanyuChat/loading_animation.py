# loading_animation.py
import sublime
import sublime_plugin

class LoadingAnimation:
    def __init__(self, view, source_view):
        self.view = view
        self.source_view = source_view
        self.message = "正在处理您的请求，请稍候... \n\n(此窗口会在完成后自动关闭)"
        self.symbols = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        self.animate_index = 0
        self.active = True
        
    def start(self):
        """启动加载动画"""
        self.active = True
        self.animate_index = 0
        self.update_animation()
        
    def stop(self):
        """停止加载动画"""
        self.active = False
        # 关闭加载视图
        if self.view and self.view.window():
            sublime.status_message("关闭加载视图")
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")
        # 聚焦原视图
        self.source_view.window().focus_view(self.source_view)
        
    def update_animation(self):
        """更新动画帧"""
        if not self.active or not self.view.is_valid():
            return
            
        # 创建动画内容
        content = "{} {}".format(
            self.symbols[self.animate_index],
            self.message
        )
        
        # 更新视图内容
        self.view.run_command("replace_content", {"content": content})
        
        # 更新索引
        self.animate_index = (self.animate_index + 1) % len(self.symbols)
        
        # 100毫秒后再次更新动画
        sublime.set_timeout(self.update_animation, 100)