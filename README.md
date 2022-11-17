# snow_plume_bot

![maven](https://img.shields.io/badge/python-3.8%2B-blue)
<a href="https://github.com/nonebot/nonebot2">
  <img src="https://img.shields.io/badge/nonebot-2.0.0-yellow">
</a>
<a href="https://github.com/Mrs4s/go-cqhttp">
  <img src="https://img.shields.io/badge/go--cqhttp-1.0.0-red">
</a>

引用声明：本项目基于[Nonebot2](https://github.com/nonebot/nonebot2)以及[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)开发，代码仅供学习交流使用

## 本地部署
1. 在本地/服务器端配置python环境
2. 在命令行输入 `pip install nb-cli` 安装nonebot2库
3. 在 https://github.com/Mrs4s/go-cqhttp 的Release中下载适合系统的版本，运行后选择 `3-反向Websocket代理`，并修改生成配置文件
4. 将本库中的所有文件下载到本地后，更改 `config.yml` 中的账号密码等bot配置信息
5. 在运行 `go-cqhttp.bat` 的前提下使用命令行输入 `nb run` 或打开 `bot.py` 以运行bot
   
## 功能
### 2022/11/07 Ver 0.9.0
* 获取涩图&nbsp; `[来/整/搞][点/张][色/涩/瑟]图` &ensp;~~涩涩是第一生产力~~
* 搜索涩图信息&nbsp; `[搜]` &ensp;~~涩涩还是第一生产力~~
* 进行运势抽签&nbsp; `[查询/看看/今日] [运势/运气] [如何/怎么样]` &ensp;~~每日1d100(?)check~~
* 计算抽卡结果&nbsp; `/抽卡 [卡池类型] [抽数] [期望结果]` &ensp;~~现实只有出货和沉船又有什么好算的呢~~

具体指令请参见[原仓库](https://github.com/wadanoharine/snow_plume-bot)下不同分支下的说明

## 开发计划
* 定时发送涩图&ensp; ~~涩涩果然是第一生产力~~
* 自动转发各平台关注用户动态
* 根据消息内容回复表情包
