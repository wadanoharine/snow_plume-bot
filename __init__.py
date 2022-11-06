# 定义事件响应器
from nonebot import on
# 添加处理依赖
from nonebot.params import EventMessage
from nonebot.adapters import Event,Message
from nonebot import rule
# 添加功能所需模块
import random
import time
import re

# 功能中重复使用的函数
# 暂无


# 插件主体：涩图 get
# 当用户在对话框输入想看涩图的信息后，轻雪酱会识别并返回“涩图 get”

    # 编写规则
async def message_checker_setu_get(event:Event):
    # 从事件中提取消息纯文本
    msg = event.get_plaintext()
    # 关键词列表
    target_pattern_list = ['.上好！',
                        '.*[来整搞][张点](.*)[色涩瑟]图.?',
                        '[^(不可以)]*(色色|涩涩|瑟瑟)！?$',
                        '让我(看看|康康|访问)！?$']
    # 匹配过程
    rule_result = False
    for pattern in target_pattern_list:
        if re.match(pattern,msg):
            rule_result = True
            break
    return rule_result
    # 生成规则（如有多个checker子规则，用逗号隔开）
rule_setu_get = rule.Rule(message_checker_setu_get)

    # 事件响应器配置
setu_get_matcher = on(type="message",rule=rule_setu_get,priority=5,block=True)

    # 功能主体
@ setu_get_matcher.handle()
async def handling(msg: Message = EventMessage()):
    msg = msg.extract_plain_text()          #获取命令信息
    if "上好！" in msg:     #每日涩图
        await setu_get_matcher.finish("涩图 get")
    elif "！" in msg:       #日常对话
        time.sleep(1)
        await setu_get_matcher.send("好啦好啦就让你色色吧！")
        time.sleep(2)
        await setu_get_matcher.send("涩图 get")
        time.sleep(7)
        await setu_get_matcher.finish("要注意节制喵")
    else:
        prob = random.randint(1,100)
        if prob >= 50:
            await setu_get_matcher.send("检测到色色能量！")
            time.sleep(2)
        if prob <= 90:
            await setu_get_matcher.send("允许色色！")
            time.sleep(1)
            await setu_get_matcher.finish("涩图 get")
        else:
            await setu_get_matcher.finish("哼！不可以色色！")


