# 声明插件依赖
from nonebot import require
require("nonebot_plugin_apscheduler")

# 从插件中导入scheduler对象
from nonebot_plugin_apscheduler import scheduler

# 发送信息
from nonebot import get_bot

# 导入定时任务中需要用到的模块
import requests
import json
from time import sleep
from random import gauss,randint
from datetime import datetime,timedelta,time


# 时间参数初始化
today = datetime.date(datetime.today())     # 初始化今天日期
weekday = datetime.now().strftime("%A")     # 初始化今天星期
wake_up_time = datetime.now()               # 初始化轻雪酱起床时间


# 通用函数一：每日1点重置参数和事件
@scheduler.scheduled_job(trigger="cron", hour="01",minute="00",timezone='Asia/Shanghai',id="routine")   
async def weekday_update():
    global today,weekday,jitter
    # 更新时间参数
    today = datetime.date(datetime.today())     # 更新今天日期
    weekday = datetime.now().strftime("%A")     # 更新今天星期
    # 设定当日轻雪酱起床时间
    Sunrise_time = get_api(["三日天气预报"])[0]['daily'][0]['sunrise']     # 获取日出时间
    jitter = gauss(0,8)                                                   # 设置起床偏差
    wake_up_time = datetime.combine(datetime.today(),datetime.time(datetime.strptime(Sunrise_time,"%H:%M") + timedelta(minutes=jitter)))     # 日出时间+起床偏差组合成为起床时间
    scheduler.add_job(morning_report,trigger="date",run_date=wake_up_time,timezone='Asia/Shanghai',id="morning_report")                      # 添加当天的晨间预报任务
    # 设定当日突击涩涩时间
    times = randint(1,4)                        # 每日1-4次突击涩涩
    hour_list = []
    for i in range(times):
        hour = randint(8,21)
        if hour not in hour_list:               # 同一小时最多只出现一次
            ero_time = datetime.combine(datetime.today(),time(hour=hour,minute=randint(0,59),second=randint(0,59)))
            scheduler.add_job(pop_ero,trigger="date",run_date=ero_time,timezone='Asia/Shanghai',id=f"ero_time{i}")
            hour_list.append(hour)
        else:
            i = i-1
            continue
    pass

# 通用函数二：从和风天气api中获取天气数据
def get_api(request_list):
    key = "9c5f09dc9c2a428faf8e430f8d8e9e4b"    # 和风天气的API key
    location = "101020100"                      # 上海市位置代码（其他城市位置代码可从和风天气开发文档中获取）
    url_dict = {
        "三日天气预报":"https://devapi.qweather.com/v7/weather/3d?",
        # 日出日落sunrise/sunset；月出月落moonrise/moonset；月相moonPhase(含moonPhaseIcon)；
        # 最值气温tempMax/tempMin；天气textDay/textNight(含iconDay/iconNight)
        # 风向windDirDay/windDirNight；风力等级windScaleDay/windScaleNight；风速windSpeedDay/windSpeedNight；
        # 当天总降水量precip；紫外线强度指数uvIndex；相对湿度humidity；大气压强pressure；能见度vis；云量cloud
        "实时天气预报":"https://devapi.qweather.com/v7/weather/now?",
        # 当前温度temp；体感温度feelslike；天气text(含icon)
        # 风向windDir；风力windScale；风速windSpeed
        # 相对湿度humidity；当前小时累计降水量precip
        # 大气压强pressure；能见度vis；云量cloud；露点温度dew
        "逐小时预报":"https://devapi.qweather.com/v7/weather/24h?",
        # 预报所处时间fxTime
        # 温度temp；天气text(含icon)
        # 风向windDir；风力windScale；风速windSpeed
        # 相对湿度humidity；当前小时累计降水量precip；当前小时降水概率pop
        # 大气压强pressure；云量cloud；露点温度dew
        "实时空气质量":"https://devapi.qweather.com/v7/air/now?",
        # 空气质量指数aqi；空气质量指数级别category；空气主要污染物primary(空气质量为优时返回NA)
        # PM10:pm10, PM2.5:pm2p5, 二氧化氮:no2, 二氧化硫:so2, 一氧化碳co, 臭氧o3
        "空气质量每日预报":"https://devapi.qweather.com/v7/air/5d?",
        # 预报所处日期fxDate
        # 空气质量指数aqi；空气质量指数级别category；空气主要污染物primary(空气质量为优时返回NA)
        "天气指数预报":"https://devapi.qweather.com/v7/indices/3d?type=0&",
        # type 1-16分别为：1.运动指数 2.洗车指数 3.穿衣指数 4.钓鱼指数 5.紫外线指数 6.旅游指数 7.过敏指数 8.舒适度指数 9.感冒指数 10.空气污染扩散条件指数 11.空调开启指数 12.太阳镜指数 13.化妆指数 14.晾晒指数 15.交通指数 16.防晒指数
        # 预报所处日期date；生活指数类型type；生活指数类型名称name
        # 生活指数预报等级level；等级描述category；详细描述text
        "天气灾害预警":"https://devapi.qweather.com/v7/warning/now?"
        # ID：id
        # 预警发布单位sender；发布时间pubTime；标题title；
        # 预警开始/结束时间startTime/endTime；发布状态status
        # 预警严重等级severity；预警类型名称typeName；预警详细文字描述text
        }
    result = []
    for req in request_list:
        url = "".join((url_dict[req],"location=",location,"&key=",key))     # 拼接request的api
        result_raw = requests.get(url)                                      # 发起请求
        result_seg = json.loads(result_raw.text)                            # 将返回结果转为json格式
        result.append(result_seg)                                           # 存入result列表中
    return result

# 通用函数三：封装并发送消息(支持解析CQ码)，返回发送消息的消息ID列表
async def sending_message(msg_list):
    msg_package = []
    msg = {"group_id": 670404622,               # 输入群号
           "message" : "",
           "auto_escape":False}                  # 设置是否不对文本中包含的CQ码进行转换
    # 将消息封装进msg字典后，放入package等待发送
    for msg_seg in msg_list:          
        msg["message"] = msg_seg
        msg_package.append(msg.copy())
    # 发送消息并获取发送消息的消息ID
    bot = get_bot()
    message_ID_list = []                             
    for msg in msg_package:
        msg_ID = await bot.call_api('send_group_msg',**msg)
        message_ID_list.append(msg_ID['message_id'])
        sleep(2)
    return message_ID_list


# 定时任务一：每晚预报次日天气

@scheduler.scheduled_job(trigger="cron",hour="22",minute="00",timezone='Asia/Shanghai',id="night_report")
async def night_report():
    msg_list = []
    greetings_night = {
        "Monday"   : "晚上好！休息的时间到了哟！\n\n    新一周的第一天就要结束了，有没有干劲满满地完成今天的工作呢？\n    即使没有干劲也没关系，疲惫也是旅途收获的一部分。\n    所以现在，就请主人好好地享受休息时间吧！让轻雪酱来为你预报明日天气：",
        "Tuesday"  : "晚上好！轻雪酱来预报明天天气啦！",
        "Wednesday": "晚上好！休息的时间到了哟！\n\n    主人今天过得如何呢？轻雪酱今天一天都陪伴在主人身边，感觉非常开心呢！如果主人也是这样想的话...\n    好！要开始预报天气了喔：",
        "Thursday" : "晚上好！休息的时间到了哟！\n\n    一天过得真快呢，总感觉今天才刚刚开始，太阳就已经落下了...主人也是这么觉得的吗？\n    好了！接下来是明天的天气预报：",
        "Friday"   : "晚上好！休息的时间到了哟！\n\n    明天开始就是周末了，主人有没有什么计划呢？轻雪酱的话，这周和朋友约了去锦江乐园玩喔！因为充满了期待，感觉晚上要兴奋地睡不着了，嘿嘿嘿...\n    好！明天的天气是：",
        "Saturday" : "晚上好！轻雪酱来预报明天天气啦！",
        "Sunday"   : "一周就要结束了，时间过得真快。晚上好！轻雪酱来预报明天天气啦！"
    }
    # 获取结果
    request_list = ("三日天气预报","天气指数预报")
    result = get_api(request_list)
    weather_tommorow = result[0]['daily'][1]['textDay']         # 次日天气
    temp_Max_tommorow = result[0]['daily'][1]['tempMax']        # 次日最高气温
    temp_Min_tommorow = result[0]['daily'][1]['tempMin']        # 次日最低气温
    wind_tommorow = result[0]['daily'][1]['windScaleDay']       # 次日风力等级
    sport_tommorow = result[1]['daily'][16]['category']         # 次日运动指数
    cold_tommorow = result[1]['daily'][24]['category']
    # 结果格式化
    weather_report = f'{today+timedelta(days=1)}\n天气：{weather_tommorow}  ({temp_Min_tommorow}℃~{temp_Max_tommorow}℃)\n风力等级：{wind_tommorow}级\n运动指数：{sport_tommorow}\n感冒指数：{cold_tommorow}'
    # 封装消息
    msg_list.append(greetings_night[weekday])
    msg_list.append(weather_report)
    # 寒潮/热浪预警
    if float(result[0]['daily'][0]['tempMin']) - float(result[0]['daily'][1]['tempMin']) >= 8:
        msg_list.append("明天会冷很多喔！请多加衣服，注意保暖吧！")
    elif float(result[0]['daily'][1]['tempMax']) - float(result[0]['daily'][0]['tempMax']) >= 8:
        msg_list.append("明天会比今天热一些喔！请提前搭配好合适的衣物吧！")
    await sending_message(msg_list)



# 定时任务二：晨间预报当日天气

async def morning_report():
    msg_list = []

    # 早起/晚起特殊对话
    special_wake_up_bool = False
    special_wake_up = ""
    if jitter > 15.2:       # 触发条件：起床偏差值达到15.2分钟(1.9个标准差，发生概率约2.87%)以上
        special_wake_up = "唔呃呃...不小心睡过头了...得赶快给主人播报天气才行......"
        special_wake_up_bool = True
    elif jitter < -15.2:
        special_wake_up = "今天的轻雪酱超有干劲呢！早早地醒来为主人播报天气喔！"
        special_wake_up_bool = True
        
    # 日常问候
    greetings_morning = {
        "Monday"   : f'早上好！今天是{today.month}月{today.day}日',
        "Tuesday"  : f'早上好！今天是{today.month}月{today.day}日',
        "Wednesday": f'早上好！今天是{today.month}月{today.day}日',
        "Thursday" : f'早上好！今天是{today.month}月{today.day}日，轻雪酱和主人说早安啦！诶，主人还在睡梦中？嘿嘿嘿...准备完天气播报，就偷偷拍一张主人睡觉的样子吧！',
        "Friday"   : f'早上好！今天是{today.month}月{today.day}日，也是工作日的最后一天，所以也请提起干劲加油吧！轻雪酱会在背后一直支持主人的！就从每天早晨的天气播报开始~',
        "Saturday" : f'早上好！今天是{today.month}月{today.day}日',
        "Sunday"   : f'早上好！今天是{today.month}月{today.day}日'
    }

    # 获取天气数据，准备天气播报
    request_list = ("实时天气预报","实时空气质量","逐小时预报")
    result = get_api(request_list)

    # 1.极端天气状况预警（水平能见度、大风预警）
    warning_bool = False
    warning_report = ""
    # 1.1 水平能见度预警(2km以下)
    vision = float(result[0]['now']['vis'])               # 获取当前水平能见度
    if vision <= 2:
        if vision <= 1:
            if vision <= 0.5:
                warning_report = "".join((warning_report,f'唔啊啊..外面伸手不见五指呢...现在的能见度只有{vision*1000:.0f}m了，'))
            else:
                warning_report = "".join((warning_report,f'今天的雾有点浓，现在的能见度只有{vision*1000:.0f}m了，'))
        else:
            warning_report = "".join((warning_report,f'外面视野不太好呢，现在的能见度只有{vision:.0f}km了，'))
        warning_bool = True
    # 1.2 大风预警(4级风及以上)
    wind_speed = float(result[0]['now']['windSpeed'])     # 获取当前风速
    if wind_speed >= 20:
        if warning_bool:
            warning_report = "".join((warning_report,'而且'))
        if wind_speed >= 29:
            if wind_speed >= 39:
                warning_report = "".join((warning_report,f'轻雪酱要被风吹跑啦！现在的风速已经达到{wind_speed}km/h了！'))
            else:
                warning_report = "".join((warning_report,f'今天的风超级大！风速已经达到{wind_speed}km/h了！'))
        else:
            warning_report = "".join((warning_report,f'今天的风有点大呀，风速达到{wind_speed}km/h了，'))        
        warning_bool = True        
    warning_report = "".join((warning_report,"主人如果出门的话，一定要注意安全呀！\n\n接下来是今天的天气情况："))

    # 2.今日天气情况预报（降水情况，空气质量）
    weather_report = "    "
    # 2.1 降水情况预报
    weather_of_hour = result[2]['hourly']                 # 获取今日逐小时天气情况
    # 数据预处理1：从结果中提取某时间点的降水量，以(fxTime,precip)形式存放在raw_dict列表中
    raw_dict = []                 
    for seg in weather_of_hour:
        fxTime = int(seg['fxTime'].split("T")[1].split(":")[0])
        precip = float(seg['precip'])
        if fxTime == 0:           # 只统计当日数据
            fxTime = 24
            precip_of_hour = (fxTime,precip)
            raw_dict.append(precip_of_hour)
            break
        precip_of_hour = (fxTime,precip)
        raw_dict.append(precip_of_hour)
    # 数据预处理2：进一步抽取天气变化情况 (晴->雨 or 雨->晴)，以(time,convert_type)形式存放在weather_change列表中
    weather_change = []             # (convert_type:-1代表由雨转晴，1代表由晴转雨)
    sum = 0
    product = 0
    for i in range(1,len(raw_dict)):
        sum = raw_dict[i][1]+raw_dict[i-1][1]                   
        product = raw_dict[i][1]*raw_dict[i-1][1]
        if sum > 0 and product == 0:                # 如果相邻两数之和>0，而乘积=0，则说明天气有变化
            if raw_dict[i][1] == 0:
                time_of_clearing_up = (raw_dict[i][0],-1)
                weather_change.append(time_of_clearing_up)
            else:
                time_of_raining = (raw_dict[i][0],1)
                weather_change.append(time_of_raining)
    # 分情况将预报对话整理进weather_report字符串
    percip_now = raw_dict[0][1]
    if len(weather_change) == 0:                # 情况一：一整天都下雨/不下雨
        if percip_now:
            weather_report = "".join((weather_report,"今天下雨会下一整天"))
        else:
            weather_report = "".join((weather_report,"今天一天都天晴"))
    elif len(weather_change) == 1:              # 情况二：现在下雨，但某个时间后会放晴（现在放晴，但某个时间会下雨）
        if percip_now:
            weather_report = "".join((weather_report,f'现在虽然在下雨，不过自{weather_change[0][0]}点起天就会放晴'))
        else:
            weather_report = "".join((weather_report,f'现在虽然天晴，不过自{weather_change[0][0]}点起就会开始下雨，主人如果要出门的话，就请带好伞吧！'))
    elif len(weather_change) >= 2:              # 情况三：天气在一天内多次变化
        if percip_now:                  
            weather_report = "".join((weather_report,f'现在虽然在下雨，不过{weather_change[0][0]}点后雨会停，随后'))
        else:                 
            weather_report = "".join((weather_report,'现在虽然天晴，不过'))
        for i in range(len(weather_change)):
            if weather_change[i][1] == 1:
                try:
                    weather_report = "".join((weather_report,f'{weather_change[i][0]}-{weather_change[i+1][0]-1}点,'))    
                except:
                    weather_report = "".join((weather_report,f'{weather_change[i][0]}点之后都-'))
        weather_report = weather_report[:-1]
        weather_report = "".join((weather_report,"会下雨。主人如果要出门的话，就请带好伞吧！"))
    # 2.2 空气质量预报
    weather_report = "".join((weather_report,"\n"))
    air_quality = result[1]['now']                      # 获取空气质量

    weather_report = "".join((weather_report,f'    另外，当前AQI指数为{air_quality["aqi"]}，达到了{air_quality["category"]}的水平，'))
    if int(air_quality["level"]) >= 3:                  # 空气质量为轻度污染以下的特殊对话
        weather_report = "".join((weather_report,"请主人适当地减少户外活动喔！"))
    else:
        weather_report = "".join((weather_report,"轻雪酱要大口呼吸新鲜空气~"))
    
    # 封装消息(消息优先级：天气预警 > 特殊起床对话 > 常规问候，随后进行天气播报)
    if warning_bool:
        msg_list.append(warning_report)
    elif special_wake_up_bool:
        msg_list.append(special_wake_up)
    else:
        msg_list.append(greetings_morning[weekday])
    msg_list.append(weather_report)

    # 发送消息
    await sending_message(msg_list)



# 定时任务三：降雨/天气灾害预警(每10分钟探测一次)

alarm_last_list = []
alarm_last_msg_ID = None
@scheduler.scheduled_job(trigger="interval",minutes = 10,timezone='Asia/Shanghai',id="weather_alarm")
async def weather_alarm():
    global alarm_last_list,alarm_last_msg_ID
    request_list = ["天气灾害预警"]
    result = get_api(request_list)
    alarm_list = result[0]['warning']
    if alarm_list == alarm_last_list:       # 如收到的预警信息和十分钟前收到的一致，则不做响应
        pass
    elif alarm_list != alarm_last_list:     # 如收到的预警信息和十分钟前不同，则进入响应处理流程
        msg_list = []
        if not alarm_list:            # 情况1：alarm_list为空，说明之前出现的所有警报都已消除了               
            try:
                msg_list.append(f"[CQ:reply,id={alarm_last_msg_ID[1]}]滴滴！所有天气预警已解除，天气恢复正常啦~")
            except:
                msg_list.append("滴滴！所有天气预警已解除，天气恢复正常啦~")
            finally:
                await sending_message(msg_list)
                alarm_last_msg_ID = None                            # 清空发送预警消息的消息ID
        else:
            if not alarm_last_list:   # 情况2：alarm_last_list为空，说明所有出现的警报都是新警报
                msg_list.append("滴滴！轻雪酱收到一则天气预警：")
                for alarm in alarm_list:
                    msg_list.append(alarm['text'])
            else:                     # 情况3：两者均不为空，说明有警报更替
                try:
                    msg_list.append(f"[CQ:reply,id={alarm_last_msg_ID[1]}]滴滴！轻雪酱收到了天气预警更新通知，最新预警如下：")      # 重启后alarm_last_msg_ID丢失，会报错
                except:
                    msg_list.append("滴滴！轻雪酱收到了天气预警更新通知，最新预警如下：")
                finally:
                    for alarm in alarm_list:
                        msg_list.append(alarm['text'])
            msg_list.append("主人出门的话，要注意安全喔！")   
            alarm_last_msg_ID = await sending_message(msg_list)     # 记录发送预警消息的消息ID
        # 记录本次预警信息
        alarm_last_list = alarm_list

            
# 定时任务四：随机时间涩涩

async def pop_ero():
    msg_list = ["突击涩涩时间！主人工作辛苦啦，工作之余也不要忘记涩涩哦！","涩图 get"]
    await sending_message(msg_list)
    