import sublime
import sublime_plugin
import threading
import time
import codecs  # 添加codecs模块用于增量解码
import json

from .loading_animation import LoadingAnimation
from .get_connection import GetConnection

class QuanyuChatStream(sublime_plugin.TextCommand):
	
    # 流式响应状态标志
    is_streaming = False
    # loading中
    start_flag = True;
    # 使用字节缓冲区
    buffer = b""
    # UTF-8增量解码器
    decoder = None  
    # 正在思考
    is_thinking = False
    # 记录<thinking>标签的起始位置
    thinking_start_pos = None

    def run(self, edit):
        self.start_flag = True
        self.is_thinking = False
        self.buffer = b""  # 重置缓冲区
        self.decoder = codecs.getincrementaldecoder('utf-8')(errors='<错误>')  # 创建解码器

        self.loading_animation = LoadingAnimation(self.view)
        self.loading_animation.start()

        sublime.status_message("启动后台线程")
        # pos = self.view.size()
        self.is_streaming = True
        threading.Thread(target=self.openAI_stream,).start()

    def openAI_stream(self):
        """流式请求API"""
        try:
            conn = GetConnection(self.view).get(True);
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
                    event = event_bytes.decode('utf-8', errors='<错误>')
                    buffer = buffer[index:]

                    # 检查事件类型
                    if event.startswith("data:"):
                        event_data = event[5:].strip()
                        # print(event_data)
                        # 检查是否结束
                        if event_data == "[DONE]":
                            self.is_streaming = False
                            return
                        
                        try:
                            # 解析JSON
                            json_data = json.loads(event_data)
                            choices = json_data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})

                                content = delta.get("reasoning_content", "")
                                if content and not self.is_thinking:
                                    self.append_stream_chunk("<thinking>\n", True)
                                    self.is_thinking = True
                                if not content:
                                    content = delta.get("content", "")
                                    if content and self.is_thinking:
                                        self.append_stream_chunk("\n<\\thinking>\n\n", False)
                                        # 计算折叠区域
                                        end_pos = self.view.size()
                                        fold_region = sublime.Region(self.thinking_start_pos, end_pos)
                                        # 在主线程执行折叠操作
                                        sublime.set_timeout(lambda: self.fold_thinking_region(fold_region), 0)

                                        self.is_thinking = False;
                                        self.thinking_start_pos = None  # 重置起始位置
                                if content:
                                    # 关闭Loading
                                    self.loading_animation.stop()
                                    sublime.status_message("⌛ 正在输出......")
                                    self.append_stream_chunk(content, False)

                            usage = json_data.get("usage", {})
                            if usage:
                                self.prompt_tokens = usage.get("prompt_tokens");
                                self.completion_tokens = usage.get("completion_tokens");
                        except json.JSONDecodeError as e:
                        	sublime.status_message(str(e))
                    # 短暂休眠以减少CPU使用
                    time.sleep(0.01)
        except Exception as e:
            # 关闭Loading
            self.loading_animation.stop()
            self.append_stream_chunk("\n\n请求失败: {}".format(str(e)), False)
        finally:
            try:
                if conn:
                    conn.close()
            except:
                pass
            self.finish_streaming(self.view.size())

    
    """追加流式内容块"""
    def append_stream_chunk(self, chunk, is_start):
        # 插入assistant标记
        if self.start_flag:
            self.view.run_command("insert_text_at_end", {
                "text": '\n\nassistant:\n'
            })
            self.start_flag = False

        sublime.set_timeout(lambda: 
            self.view.run_command("insert_text_at_end", {
                "text": chunk
            }), 0)
        
        # 在主线程插入文本
        if is_start:
            self.thinking_start_pos = self.view.size() + 11

        # 滚动视图
        sublime.set_timeout(lambda: self.view.show(self.view.size()), 0)

    def finish_streaming(self, original_pos):
        # 插入token花费情况和用户输入提示
        sublime.set_timeout(lambda: 
            self.view.run_command("insert_text_at_end", {
                "text": '\n\n↑ {}  ↓ {}\n\n\nuser:\n'.format(self.prompt_tokens, self.completion_tokens)
            }), 0)
        
        # 更新状态
        sublime.status_message("✅ DeepSeek AI 已完成响应")

    def fold_thinking_region(self, region):
        if region.a >= region.b:
            return
        self.view.unfold(region)  # 先展开可能存在的嵌套折叠
        self.view.fold(region)    # 执行折叠
        self.view.show(region)    # 确保区域可见
        # 设置区域为可折叠块（关键步骤）
        self.view.add_regions(
            "folded_content",
            [region],
            scope="region.bluish",
            flags=sublime.DRAW_NO_FILL
        )