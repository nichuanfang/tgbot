import telebot
import requests
from settings.config import dogyun_config
from datetime import datetime
from datetime import date
from flask_apscheduler import APScheduler
from bs4 import BeautifulSoup
import lxml

DOGYUN_WEBHOOK_URL_PATH = "/%s/" % (dogyun_config['BOT_TOKEN'])

logger = telebot.logger

bot = telebot.TeleBot(dogyun_config['BOT_TOKEN'],threaded=False)

scheduler = APScheduler()

@bot.message_handler(commands=['server_info'])
def get_server_status(message):
    """获取服务器状态

    Returns:
        _type_: _description_
    """    
    url = f'https://api.dogyun.com/cvm/server/{dogyun_config["DOGYUN_SERVER_ID"]}'
    headers = {
        'API-KEY': dogyun_config['DOGYUN_API_KEY']
    }
    # GET请求
    try:
        response = requests.get(url, headers=headers,verify=True)
    except Exception as e:
        bot.reply_to(message, f'获取服务器状态失败: {e.args[0]}')
        return
    # 获取返回的json数据
    data = response.json()
    # 获取服务器状态
    if data['success']:
        server_info = data['data']
        # 获取服务器健康状态
        health = server_info['health']
        ip = server_info['ipv4']
        # cpu
        cpu = round(health['cpu']/health['maxcpu']*100,2)
        # 内存
        memory = round(health['mem']/health['maxmem']*100,2)
        bot.reply_to(message, f'IP:  {ip}\n状态:  {data["data"]["status"]}\nCPU:  {cpu}%\n内存:  {memory}%')
    else:
        bot.reply_to(message, '获取服务器状态失败')

@bot.message_handler(commands=['traffic_info'])
def send_traffic_info(message):
    """流量详情

    Args:
        message (_type_): _description_
    """   
    url = f'https://api.dogyun.com/cvm/server/{dogyun_config["DOGYUN_SERVER_ID"]}/traffic'
    headers = {
        'API-KEY': dogyun_config['DOGYUN_API_KEY']
    }
    try:
        # GET请求
        response = requests.get(url, headers=headers,verify=True)
        # 获取返回的json数据
        data = response.json()
    except Exception as e:
        bot.reply_to(message, f'获取流量详情失败: {e.args[0]}')
        return
    # 获取流量信息
    traffic_info = data['data'][-1]
    # 被动流入
    inputIn = round(traffic_info['inputIn']/1000/1000,2)
    # 被动流出
    inputOut = round(traffic_info['inputOut']/1000/1000,2)
    # 主动流入
    outputIn = round(traffic_info['outputIn']/1000/1000,2)
    # 主动流出
    outputOut = round(traffic_info['outputOut']/1000/1000,2)
    # 总计(保留两位小数)
    total = round((traffic_info['inputIn'] + traffic_info['inputOut'] + traffic_info['outputIn'] + traffic_info['outputOut'])/1000/1000/1000,2)
    bot.reply_to(message, f'总计:{total}GB\n\n被动流入:{inputIn}MB\n被动流出:{inputOut}MB\n主动流入:{outputIn}MB\n主动流出:{outputOut}MB')


@bot.message_handler(commands=['receive_monthly_benefits'])
def receive_monthly_benefits(message):
    """领取每月流量包

    Args:
        message (_type_): _description_
    """ 
    url = f'https://cvm.dogyun.com/traffic/package/level'
    headers = {
        'X-Csrf-Token': dogyun_config['DOGYUN_CSRF_TOKEN'],
        'Origin': 'https://cvm.dogyun.com',
        'Referer': 'https://cvm.dogyun.com/traffic/package/list',
        'Cookie': dogyun_config['DOGYUN_COOKIE']
    }
    try:
        # 发送post请求
        response = requests.post(url, headers=headers,verify=True)
    except Exception as e:
        bot.reply_to(message, f'领取每月流量包失败: {e.args[0]}')
        return
    # 获取返回的json数据
    try:
        data = response.json()
    except:
        # tg通知dogyun cookie已过期
        bot.reply_to(message, 'dogyun cookie已过期,请更新cookie')
        return
    # 获取领取结果
    result = data['message']
    bot.reply_to(message, result)
    

@bot.message_handler(commands=['draw_lottery'])
def draw_lottery(message):
    """抽奖(待完善)

    Args:
        message (_type_): _description_
    """    
    pass

# 每月7号
@scheduler.task('cron', id='get_traffic_packet', month='*', day='*', hour='12', minute='25', second='0')
def get_traffic_packet():
    """自动领取流量包
    """    
    url = f'https://cvm.dogyun.com/traffic/package/level'
    headers = {
        'X-Csrf-Token': dogyun_config['DOGYUN_CSRF_TOKEN'],
        'Origin': 'https://cvm.dogyun.com',
        'Referer': 'https://cvm.dogyun.com/traffic/package/list',
        'Cookie': dogyun_config['DOGYUN_COOKIE']
    }
    try:
        # 发送post请求
        response = requests.post(url, headers=headers,verify=True)
    except Exception as e:
        # tg通知dogyun cookie已过期
        bot.send_message(dogyun_config['CHAT_ID'], f'领取流量包失败: {e.args[0]}!')
        return
    try:
        data = response.json()
    except:
        # tg通知dogyun cookie已过期
        bot.send_message(dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie!')
        return
    # 获取领取结果
    result = data['message']
    # 获取当前时间
    now = datetime.now()
    # 获取当前日期
    today = date.today()
    # 获取当前时间
    current_time = now.strftime("%H:%M:%S")
    # 获取当前日期
    current_date = today.strftime("%Y-%m-%d")
    # 记录日志
    logger.info(f'{current_date} {current_time} {result}')
    # 发送通知
    bot.send_message(dogyun_config['CHAT_ID'], f'等级奖励通用流量包: {result}')

# 每天获取通知
@scheduler.task('cron', id='lucky_draw_notice', month='*', day='*', hour='9', minute='0', second='0')
def lucky_draw_notice():
    """抽奖活动通知
    """ 
    url = f'https://console.dogyun.com/turntable'
    headers = {
        'Cookie': dogyun_config['DOGYUN_COOKIE'],
        'Referer': 'https://member.dogyun.com/',
        'Origin': 'https://console.dogyun.com',
        'X-Csrf-Token': dogyun_config['DOGYUN_CSRF_TOKEN']
    }
    try:
        # 发起get请求
        response = requests.get(url, headers=headers,verify=True)
    except Exception as e:
        bot.send_message(dogyun_config['CHAT_ID'], f'抽奖活动通知失败: {e.args[0]}!')
        return
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    result = soup.find('h2',class_='mb-0 text-center').text
    if result is None or result == '':
        bot.send_message(dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie!')
        return
    if result == '暂无抽奖活动':
        pass
    else:
        bot.send_message(dogyun_config['CHAT_ID'], f'抽奖活动通知: {result}')
        logger.info(f'抽奖活动通知: {result}')
        

def webhook(app,flask,FLASK_URL_BASE):
    """设置webhook
    """    
    # Set webhook
    @app.route('/dogyun')
    def home():
        # 设置webhook
        bot.remove_webhook()
        # Set webhook
        bot.set_webhook(url=FLASK_URL_BASE + DOGYUN_WEBHOOK_URL_PATH,max_connections=1)
        return 'dogyun-Webhook设置成功!'

        
    # Process webhook calls
    @app.route(DOGYUN_WEBHOOK_URL_PATH, methods=['POST'],strict_slashes=False)
    def webhook():
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            flask.abort(403)

