import sublime
import sublime_plugin

class QuanyuHttpInit(sublime_plugin.TextCommand):
	
    def run(self, edit):
        view = self.view.window().new_file()
        config_str = "{\n    \"host\": \"\",\n    \"endpoint\": \"\",\n    \"type\": \"GET/POST\",\n    \"headers\": {\n\n    },\n    \"body\": {\n\n    },\n    \"params\": {\n\n    }\n}"
        view.run_command("insert_text_at_end", {"text": config_str})