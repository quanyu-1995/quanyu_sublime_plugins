import sublime
import sublime_plugin
import http.client
import json
import threading
import time
import codecs  # 添加codecs模块用于增量解码

from .config_utils import ConfigManager  # 导入配置管理工具
from .loading_animation import LoadingAnimation

class QuanyuChatStream(sublime_plugin.TextCommand):
	
    # 流式响应状态标志
    is_streaming = False
    # loading中
    start_flag = True;
    # 使用字节缓冲区
    buffer = b""
    # UTF-8增量解码器
    decoder = None  

    def run(self, edit):

        # 从配置中获取值
        self.api_key = ConfigManager.api_key()
        self.api_url = ConfigManager.api_url()
        self.api_endpoint = ConfigManager.api_endpoint()
        self.model = ConfigManager.model()
        self.conn_timeout = ConfigManager.conn_timeout()
        self.req_timeout = ConfigManager.req_timeout()

        self.start_flag = True
        self.buffer = b""  # 重置缓冲区
        self.decoder = codecs.getincrementaldecoder('utf-8')(errors='<错误>')  # 创建解码器


        sublime.status_message("准备数据")
        pos = self.view.size()
        region = sublime.Region(0, pos)
        text = self.view.substr(region)
        messages = self.getMessages(text)
        
        sublime.status_message("创建加载弹窗")
        self.loading_view = self.view.window().new_file()
        self.loading_view.set_name("⌛ DeepSeek AI 正在思考...")
        self.loading_view.set_scratch(True)


        self.loading_animation = LoadingAnimation(
            self.loading_view,
            self.view
        )
        self.loading_animation.start()

        sublime.status_message("启动后台线程")
        self.is_streaming = True
        threading.Thread(
            target=self.openAI_stream, 
            args=(messages, pos)
        ).start()
       
    """组装接口请求Messages参数（对话记录）"""
    def getMessages(self, text):
        arr = text.split('\n')
        content = ""
        role = "user"
        messages = []
        
        for line in arr:
            if line.startswith('system:'):
                if role:
                    messages.append({"role": role, "content": content})
                role = 'system'
                content = line.replace('system:', '', 1).strip()
            elif line.startswith('assistant:'):
                if role:
                    messages.append({"role": role, "content": content})
                role = 'assistant'
                content = line.replace('assistant:', '', 1)
            elif line.startswith('user:'):
                if role:
                    messages.append({"role": role, "content": content})
                role = 'user'
                content = line.replace('user:', '', 1)
            else:
                content += '\n' + line
                
        if content:
            messages.append({"role": role, "content": content})
            
        return messages

    def openAI_stream(self, messages, pos):
        """流式请求API"""
        try:
            # 准备请求数据
            data = {
                "model": self.model,
                "messages": messages,
                "stream": True  # 启用流式
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
            response = conn.getresponse()

            # 检查状态码
            if response.status != 200:
                error_data = response.read().decode("utf-8")
                raise Exception("Error: {} - {}".format(response.status,error_data))
            
            # 处理流式响应
            sublime.status_message("处理流式响应")
            # 使用字节缓冲区处理数据
            buffer = b""

            while self.is_streaming:
                # 读取一块数据
                chunk = response.read(1024)
                if not chunk:
                    break
                # 解码并添加到缓冲区
                buffer += chunk
                # 处理完整的事件
                while b"\n\n" in buffer:
                    # 分割事件
                    index = buffer.index(b"\n\n") + 2
                    event_bytes = buffer[:index]
                    buffer = buffer[index:]

                    try:
                        # 安全解码事件数据
                        event = event_bytes.decode('utf-8', errors='<错误>')
                    except UnicodeDecodeError:
                        # 使用更健壮的解码方式
                        event = event_bytes.decode('utf-8', errors='<错误>')
                        sublime.status_message("部分解码错误，已使用替代字符")
                    

                    # 跳过空行
                    if not event.strip():
                        continue
                    # 检查事件类型
                    if event.startswith("data:"):
                        event_data = event[5:].strip()
                        # 检查是否结束
                        if event_data == "[DONE]":
                            self.is_streaming = False
                            return
                        
                        try:
                            # 解析JSON
                            print("{}\n".format(event_data))
                            json_data = json.loads(event_data)
                            choices = json_data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    # 关闭Loading
                                    self.loading_animation.stop()
                                    sublime.status_message("⌛ 正在输出......")
                                    self.append_stream_chunk(content)
                        except json.JSONDecodeError as e:
                        	sublime.status_message(str(e))
                    # 短暂休眠以减少CPU使用
                    time.sleep(0.01)
        except Exception as e:
            # 关闭Loading
            self.loading_animation.stop()
            self.append_stream_chunk("\n\n请求失败: {}".format(str(e)))
        finally:
            try:
                if conn:
                    conn.close()
            except:
                pass
            self.finish_streaming(pos)

    def append_stream_chunk(self, chunk):
        """追加流式内容块"""

        # 插入assistant标记
        if self.start_flag:
            self.view.run_command("insert_text_at_end", {
                "text": '\n\nassistant:\n'
            })
            self.start_flag = False
        # 在主线程插入文本
        sublime.set_timeout(lambda: 
            self.view.run_command("insert_text_at_end", {
                "text": chunk
            }), 0)
        
        # 滚动视图
        sublime.set_timeout(lambda: self.view.show(self.view.size()), 0)

    def finish_streaming(self, original_pos):
        # 插入用户输入提示
        sublime.set_timeout(lambda: 
            self.view.run_command("insert_text_at_end", {
                "text": '\n\nuser:\n'
            }), 0)
        
        # 更新状态
        sublime.status_message("✅ DeepSeek AI 已完成响应")