# quanyu_sublime_plugins

Sublime Text插件合集清单

- QuanyuChat
	- 接入DeepSeek，通过Sublime实现DeepSeek对话，支持多轮对话
- QuanyuHTTP
	- 为Sublime提供GET/POST  HTTP接口调用功能
- SaoLei
	- 在Sublime中新增扫雷小游戏


## 插件使用方法

1. 下载项目中插件文件夹
2. 打开Sublime Text，进入插件目录
3. 插件目录进入方法：依次点击Preferences（首选项） -> Browse Packages…（浏览插件目录） 打开文件夹
4. 将下载好的插件放到插件目录中，即可在Sublime Text中使用该插件

## 插件说明

- QuanyuChat
	- 接入DeepSeek，通过Sublime实现DeepSeek对话，支持多轮对话
	- Quanyu Chat提供两种输出模式：
		- qyChat: DeepSeek调用完成后一次性输出，loading过程较慢
		- qyChatStream: 流式输出，实现打字机效果，随着DeepSeek的流式输出同步输出
	- 点击Preferences（首选项） -> Package Settions -> Quanyu Plugins -> QuanyuChat -> Settings 打开插件设置文件，文件说明如下：
	```json
	{
	    "api_key": "Bearer <你的DeepSeek API Key>", // API key
	    "model": "deepseek-reasoner", 		// 模型选择，deepseek-chat：deepseek-V3模型，deepseek-reasoner：deepseek-R1模型
	    // "conn_timeout": 5.0, 			// 连接超时时间，默认5s
	    // "req_timeout": 60.0			// 响应超时时间，默认60s
	}
	```
- QuanyuHTTP
	- 为Sublime提供GET/POST  HTTP接口调用功能
	- QuanyuHTTP提供两个功能：
		- qyHTTPInit： 重新打开一个页签，并初始化HTTP调用所需配置，用户只需要填写配置中的内容即可
		- qyHTTP: 选中所需调用的完整HTTP配置区域，发起调用
	- HTTP调用配置说明：
	```json
	{
	    "host": "", 	//HTTP调用host，如域名，如ip:post 
	    "endpoint": "",	//请求后缀
	    "type": "GET/POST", //请求类型，支持GET、POST请求
	    "headers": {	//请求头

	    },
	    "body": {		//请求体，POST请求参数

	    },
	    "params": {		//GET请求参数

	    }
	}
	```
