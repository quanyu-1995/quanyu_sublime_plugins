import sublime
import sublime_plugin
import http.client
import json
import threading

from .config_utils import ConfigManager  # 导入配置管理工具
from .loading_animation import LoadingAnimation


class quanyuChat(sublime_plugin.TextCommand):

	def run(self, edit):
		# 从配置中获取值
		self.api_key = ConfigManager.api_key()
		self.api_url = ConfigManager.api_url()
		self.api_endpoint = ConfigManager.api_endpoint()
		self.model = ConfigManager.model()
		self.conn_timeout = ConfigManager.conn_timeout()
		self.req_timeout = ConfigManager.req_timeout()
		# 1. 准备数据（主线程）
		pos = self.view.size()
		region = sublime.Region(0, pos)
		text = self.view.substr(region)
		messages = self.getMessages(text)
		
		# 2. 创建加载弹窗
		self.loading_view = self.view.window().new_file()
		self.loading_view.set_name("⌛ DeepSeek AI 正在思考...")
		self.loading_view.set_scratch(True)  # 设为临时文件，关闭时不提示保存

		self.loading_animation = LoadingAnimation(
			self.loading_view,
			self.view
		)
		self.loading_animation.start()

		# 4. 启动后台线程
		threading.Thread(
			target=self.fetch_openai_response, 
			args=(messages, pos)
		).start()

	# 获取messages参数
	def getMessages(self, text):
		arr = text.split('\n');

		content = "";
		role = "user";
		messages = [];
		for line in arr:
			if line.startswith('system:'):
				if(role!=""):
					messages.append({"role":role,"content":content});
				role = 'system';
				content = line.replace('system:','',1);
			elif  line.startswith('assistant:'):
				if(role!=""):
					messages.append({"role":role,"content":content});
				role = 'assistant';
				content = line.replace('assistant:','',1);
			elif line.startswith('user:'):
				if(role!=""):
					messages.append({"role":role,"content":content});
				role = 'user';
				content = line.replace('user:','',1);
			else:
				content = content + '\n' + line;
		if content:
			messages.append({"role":role,"content":content});
		return messages;

	def openAI(self, messages):
		# 1. 准备请求数据
		data={"model":self.model, "messages":messages, "stream":False}  # POST 数据
		headers = {
			"Content-Type": "application/json",
			"Authorization": self.api_key
		}
		# 2. 发送 POST 请求
		conn = None
		res = "";
		try:
			conn = http.client.HTTPSConnection(self.api_url);

			# 2. 设置连接超时（5秒）
			conn.connect()
			conn.sock.settimeout(self.conn_timeout)  # 连接超时

			conn.request("POST", self.api_endpoint, body=json.dumps(data), headers=headers)

			# 4. 设置读取超时
			conn.sock.settimeout(self.req_timeout)  # 读取超时

			# 3. 获取响应
			response = conn.getresponse()
			data = response.read().decode("utf-8")
            # 4. 处理结果（示例：显示在状态栏）
			if response.status == 200:
				res = json.loads(data)['choices'][0]['message']['content'];
			else:
				raise Exception("Error: {} - {}".format(response.status,data))
		finally:
			if conn is not None:
			    try:
			        conn.close()
			    except:
			        pass  # 即使关闭出错也不影响程序
		return res;	

	def fetch_openai_response(self, messages, pos):
		"""后台线程执行网络请求"""
		try:
			res = self.openAI(messages)
			# 将结果调度回主线程
			sublime.set_timeout(lambda: self.append_result(res, pos), 0)
		except Exception as e:
			str_e = str(e)
			sublime.set_timeout(lambda: self.append_result("请求失败: {}".format(str_e), pos), 0)

	def append_result(self, res, pos):
		"""主线程更新UI"""
		self.loading_animation.stop()
		
		# 3. 插入结果
		self.view.run_command("insert_text_at_end", {
			"text": '\n\nassistant:\n{}\n\nuser:\n'.format(res)
		})
		
		# 4. 显示完成提示
		sublime.status_message("✅ DeepSeek AI 已完成响应")