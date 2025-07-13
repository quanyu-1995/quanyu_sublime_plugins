import sublime
import sublime_plugin
import threading
import json

from .loading_animation import LoadingAnimation
from .get_connection import GetConnection


class quanyuChat(sublime_plugin.TextCommand):

	prompt_tokens = None
	completion_tokens = None

	def run(self, edit):
		self.loading_animation = LoadingAnimation(
			self.view
		)
		self.loading_animation.start()

		# 4. 启动后台线程
		threading.Thread(
			target=self.fetch_openai_response
		).start()

	def fetch_openai_response(self):
		"""后台线程执行网络请求"""
		try:
			res = self.openAI()
			# 将结果调度回主线程
			sublime.set_timeout(lambda: self.append_result(res, self.view.size()), 0)
		except Exception as e:
			str_e = str(e)
			sublime.set_timeout(lambda: self.append_result("请求失败: {}".format(str_e), self.view.size()), 0)

	def openAI(self):
		conn = None;
		res = "";
		try:
			conn = GetConnection(self.view).get(False);
			# 获取响应
			response = conn.getresponse()
			data = response.read().decode("utf-8")
            # 4. 处理结果（示例：显示在状态栏）
			if response.status == 200:
				# print(data)
				message =  json.loads(data)['choices'][0]['message']
				reasoning_content = message.get('reasoning_content');
				content = message.get('content');
				if reasoning_content:
					res = "<thinking>\n" + reasoning_content + "\n<\\thinking>\n\n" + content
				else:
					res = content
				usage = json.loads(data).get("usage")
				if usage:
					self.prompt_tokens = usage.get("prompt_tokens");
					self.completion_tokens = usage.get("completion_tokens");
			else:
				raise Exception("Error: {} - {}".format(response.status,data))
		finally:
			if conn:
			    try:
			        conn.close()
			    except:
			        pass  # 即使关闭出错也不影响程序
		return res;	

	def append_result(self, res, pos):
		"""主线程更新UI"""
		self.loading_animation.stop()

		# 3. 插入结果
		self.view.run_command("insert_text_at_end", {
			"text": '\n\nassistant:\n{}\n\n↑ {}  ↓ {}\n\n\nuser:\n'.format(res, self.prompt_tokens, self.completion_tokens)
		})
		
		# 4. 显示完成提示
		sublime.status_message("✅ DeepSeek AI 已完成响应")