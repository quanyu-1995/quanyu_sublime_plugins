# build_messages.py
import sublime
import sublime_plugin

class BuildMessages(sublime_plugin.TextCommand):

    def __init__(self, view):
	    self.view = view

    def get(self):
        pos = self.view.size()
        region = sublime.Region(0, pos)
        text = self.view.substr(region)

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