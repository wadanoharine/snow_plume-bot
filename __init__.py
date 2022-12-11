# 定义事件响应器
from nonebot import on
# 添加处理依赖
from nonebot.params import EventMessage
from nonebot.adapters import Event,Bot,Message
from nonebot import rule
# 添加功能所需模块
import random
import time
import re
from snow_plume.mysql import execute_procedure
'''
插件功能：当用户在对话框输入想看涩图的信息后，轻雪酱会识别并返回“涩图 get”
'''


# 设置响应规则
async def message_checker_setu_get(event:Event):
    msg = event.get_plaintext()         # 从事件中提取消息纯文本
    # 正则匹配消息文本
    target_pattern_list = ['.*[来整搞][张点](.*)[色涩瑟]图?.?',
                        '[^(不)]*(色色|涩涩|瑟瑟)！?$',
                        '让我(看看|康康|访问)！?$']
    rule_result = False
    for pattern in target_pattern_list:
        if re.match(pattern,msg):
            rule_result = True
            break
    return rule_result
rule_setu_get = rule.Rule(message_checker_setu_get)         # 生成规则（如有多个checker子规则，用逗号隔开）

# 配置事件响应器
setu_get_matcher = on(type="message",rule=rule_setu_get,priority=5,block=True)

# 功能主体
@ setu_get_matcher.handle()
async def handling(bot:Bot,event:Event,msg: Message = EventMessage()):
    msg = msg.extract_plain_text()          #获取命令信息
    if "！" in msg:       #日常对话
        time.sleep(1)
        await setu_get_matcher.send("好啦好啦就让你色色吧！")
        time.sleep(2)
        await setu_get_matcher.send("涩图 get")
        time.sleep(7)
        await setu_get_matcher.finish("要注意节制喵")
    else:
        # 每日首次特殊对话
        session_id = event.get_session_id().split("_")
        group_id = session_id[1]
        user_id = session_id[2]
        proc = execute_procedure('ero',[f'{user_id}',f'{group_id}'],['times_of_ero'])
        times_of_ero = proc.proc()['times_of_ero']
        if not times_of_ero:
            raw_data = await bot.call_api('get_group_member_info',**{      
                'group_id': group_id,
                'user_id' : user_id
                })
            nickname = raw_data['nickname']
            await setu_get_matcher.send(f"检测到{nickname}发出的色色请求！")
            time.sleep(2)

        prob = random.random()
        if prob <= 0.95-0.94*2**(-18/(times_of_ero+1)):
            await setu_get_matcher.finish("涩图 get")
        elif times_of_ero <= 1:
            await setu_get_matcher.finish(f"哼！总之就是不可以色色！")
        else:
            await setu_get_matcher.finish(f"今天你都色色{times_of_ero}次了，不可以色色！")


