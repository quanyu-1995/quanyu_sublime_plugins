import sublime
import sublime_plugin
import random

# 答案数组
res = None
# 初始化显示数组
show = None
# 已打开数量
found = 0;
# 雷的数量
leiCnt = 10
# 等级
lvl = 10
# 提示数字比例
warning = 0.5


class saoLei(sublime_plugin.TextCommand):
	def run(self, edit):
		global res
		global show
		global leiCnt
		global lvl
		global warning
		global found
		found = 0
		res = [['-' for _ in range(lvl)] for _ in range(lvl)]
		show = [['+' for _ in range(lvl)] for _ in range(lvl)]
		# 初始化雷
		i=0
		while i<leiCnt:
			x=random.randint(0, lvl-1)
			y=random.randint(0, lvl-1)
			if res[x][y]=='-':
				res[x][y]='*'
				i=i+1

		# 初始化提示
		warning_cnt = lvl*lvl*warning
		i=0
		while i<warning_cnt:
			x=random.randint(0, lvl-1)
			y=random.randint(0, lvl-1)
			if res[x][y]=='-':
				val = 0
				if x-1>=0 and y-1>=0 and res[x-1][y-1]=='*':
					val+=1
				if x-1>=0 and res[x-1][y]=='*':
					val+=1
				if x-1>=0 and y+1<lvl and res[x-1][y+1]=='*':
					val+=1
				if y-1>=0 and res[x][y-1]=='*':
					val+=1
				if y+1<lvl and res[x][y+1]=='*':
					val+=1
				if x+1<lvl and y-1>=0 and res[x+1][y-1]=='*':
					val+=1
				if x+1<lvl and res[x+1][y]=='*':
					val+=1
				if x+1<lvl and y+1<lvl and res[x+1][y+1]=='*':
					val+=1
				i+=1
				res[x][y]=str(val)

		# 展示
		point = 0;
		text = '';
		for arr in show:
			for t in arr:
				text+=t;
			text+='\n'
		self.view.insert(edit, 0, text)
		print(found);

class openLei(sublime_plugin.TextCommand):
	def run(self, edit):
		global res
		global show
		global leiCnt
		global lvl
		global found
		cursor_position = self.view.sel()[0].begin()
		row,col = self.view.rowcol(cursor_position)
		col-=1
		if show[row][col] == '\n':
			return
		if show[row][col] != '*':
			region = sublime.Region(cursor_position - 1, cursor_position)
			self.view.replace(edit, region, res[row][col])
			found+=1
		if res[row][col] == '*':
			text = "\n\n\n失败\n\n\n"
			self.view.insert(edit, 0, text)
		if found>= lvl*lvl-leiCnt:
			text = "\n\n\n成功\n\n\n"
			self.view.insert(edit, 0, text)
		print(found);