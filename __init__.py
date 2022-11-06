from nonebot import on

from nonebot.adapters import Bot,Event
from nonebot import rule

import random
import time
import re

# 功能中重复使用的函数
# 暂无

# 插件主体：今日运势
# 用户在对话框输入想要查看今日运势的相关讯息后，轻雪酱会识别并返回抽签的结果

async def message_checker_fortune(event:Event):
    msg = event.get_plaintext()
    pattern0 = re.compile("(运势|运气|手气|签)")    
    pattern1 = [("查","看看","测","抽"),("如何","怎么样","咋样","怎样")]
    if pattern0.findall(msg):       #要触发该功能，语句中必须含有pattern0中的词
        count = 0
        for pattern in pattern1:
            for i in pattern:       #要触发该功能，语句中还必须含有pattern1中的词
                if i in msg:
                    count += 1
                    break
        if count or msg == "今日运势" or msg == "运势":
            rule_result = True
        else:
            rule_result = False
        return rule_result

rule_fortune = rule.Rule(message_checker_fortune)

fortune_matcher = on(type="message",rule=rule_fortune,priority=5,block=True)

@ fortune_matcher.handle()
async def handling(bot:Bot,event:Event):    #要调用api，需要添加Bot对象
    session_id = event.get_session_id().split("_")                  #session_id返回了触发指令的对象信息，包括用户id和所在群组id
    raw_data = await bot.call_api('get_group_member_info',**{       #根据用户id和群组id调用go-cqhttp的“get_group_member_info”API，获取该对象的详细信息
        'group_id': session_id[1],
        'user_id' : session_id[2]
    })                                                              #go-cqhttp API调用：https://docs.go-cqhttp.org/api/
    nickname = raw_data['nickname']                                 #从详细信息中获取{“昵称”：“nickname”}

    await fortune_matcher.send("要开始抽签了喔！我看看，今天{}的运势……".format(nickname))
    time.sleep(3)

    prob = random.randint(-3,110)
    fortune_level_list = [0,9,39,69,99,110]
    greetings_list = [("诶诶，是大凶吗！？","！！\n我还是第一次见到大凶呢……今天真的没有问题吗！！？"),
    ("唔呃呃，居然是凶吗……","。\n轻雪酱会为你祈祷的！"),
    ("是末吉喔！","。\n看来今天也会拥有小幸运呢！"),
    ("是吉耶！","。\n幸运的事会发生吧？"),
    ("中吉！","。\n今天会发生什么好事呢？"),
    ("哇！是大吉诶！","！！\n现在的轻雪酱和你一样幸福！")]
    for i in range(0,6):
        if prob <= fortune_level_list[i]:
            greetings = greetings_list[i]
            await fortune_matcher.finish("{}运势指数是：{}{}".format(greetings[0],prob,greetings[1]))
