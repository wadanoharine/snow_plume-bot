# 定义事件响应器
from nonebot import on

# 添加处理依赖
from nonebot.params import EventMessage
from nonebot.adapters import Bot,Event,Message
from nonebot import rule
# 添加功能所需模块
import random
import time
import re
import json

# 涩图 get

    # 编写规则
async def message_checker_setu_get(event:Event):
    # 从事件中提取消息纯文本
    msg = event.get_plaintext()
    # 关键词列表
    target_pattern_list = ['上好！',
                           '[来整][张点](.*)[色涩瑟]图',
                           '[^(不可以)]*(色色|涩涩|瑟瑟)！?$',
                           '(看看|康康).*！',
                           '访问！']
    # 匹配过程
    rule_result = False
    for pattern in target_pattern_list:
        if re.match(pattern,msg):
            rule_result = True
            break
    return rule_result

async def id_checker_setu_get(event:Event):
    id = event.get_user_id()
    if id == "409932598":
        rule_result = False
    else:
        rule_result = True
    return rule_result        
    # 生成规则（如有多个checker子规则，用逗号隔开）
rule_setu_get = rule.Rule(message_checker_setu_get,id_checker_setu_get)

    # 事件响应器配置
setu_get_matcher = on(type="message",rule=rule_setu_get,priority=5,block=True)
    # 功能主体
@ setu_get_matcher.handle()
async def handling(msg: Message = EventMessage()):
    msg = msg.extract_plain_text()
    if "上好！" in msg:     #每日涩图
        await setu_get_matcher.send("涩图 get")
    elif "！" in msg:       #日常对话
        await setu_get_matcher.send("好啦好啦就让你色色吧！")
        time.sleep(2)
        await setu_get_matcher.send("涩图 get")
        time.sleep(7)
        await setu_get_matcher.send("要注意节制喵")
    else:
        prob = random.randint(1,100)
        if prob >= 50:
            await setu_get_matcher.send("检测到色色能量！")
            time.sleep(2)
        
        if prob <= 90:
            await setu_get_matcher.send("允许色色！")
            time.sleep(1)
            await setu_get_matcher.send("涩图 get")
        else:
            await setu_get_matcher.send("哼！不可以色色！")


# 今日运势

async def message_checker_luck(event:Event):
    msg = event.get_plaintext()
    if re.match(".*运势(查询|如何|怎么样)?$",msg):
        rule_result = True
    else:
        rule_result = False
    return rule_result

rule_luck = rule.Rule(message_checker_luck)

luck_matcher = on(type="message",rule=rule_luck,priority=5,block=True)

@ luck_matcher.handle()
async def handling(bot:Bot,event:Event):    #要调用api，需要添加Bot对象
    session_id = event.get_session_id().split("_")
    print(session_id)
    raw_data = await bot.call_api('get_group_member_info',**{       #调用go-cqhttp的API，返回回应消息对象的用户id和所在群id
        'group_id': session_id[1],
        'user_id' : session_id[2]
    })
    nickname = raw_data['nickname']                                 #go-cqhttp API调用：https://docs.go-cqhttp.org/api/

    await luck_matcher.send("要开始抽签了喔！我看看，今天{}的运势……".format(nickname))
    time.sleep(3)

    prob = random.randint(-3,110)
    luck_level_list = [0,9,39,70,100,110]
    greetings_list = [("诶诶，是大凶吗！？","！！，今天真的没有问题吗？"),
    ("唔呃呃，凶","1"),
    ("末吉","2"),
    ("小吉","3"),
    ("中吉","4"),
    ("哇！是大吉诶！","！！，")]
    for i in range(0,6):
        if prob <= luck_level_list[i]:
            greetings = greetings_list[i]
            await luck_matcher.send("{}，运势指数是：{}{}".format(greetings[0],prob,greetings[1]))
            break

