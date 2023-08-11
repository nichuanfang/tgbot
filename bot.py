import time
import telebot
import requests
from settings import config
import logging
from datetime import datetime
from datetime import date
from apscheduler.schedulers.blocking import BlockingScheduler

WEBHOOK_URL_BASE = "https://%s:%s" % (config.WEBHOOK_HOST,config.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.BOT_TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(config.BOT_TOKEN)

@bot.message_handler(commands=['traffic_info'])
def send_traffic_info(message):
    """流量详情

    Args:
        message (_type_): _description_
    """   
    url = f'https://api.dogyun.com/cvm/server/{config.DOGYUN_SERVER_ID}/traffic'
    headers = {
        'API-KEY': config.DOGYUN_API_KEY
    }
    # GET请求
    response = requests.get(url, headers=headers)
    # 获取返回的json数据
    data = response.json()
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
        'X-Csrf-Token': config.DOGYUN_CSRF_TOKEN,
        'Origin': 'https://cvm.dogyun.com',
        'Referer': 'https://cvm.dogyun.com/traffic/package/list',
        'Cookie': config.DOGYUN_COOKIE
    }
    # 发送post请求
    response = requests.post(url, headers=headers)
    # 获取返回的json数据
    data = response.json()
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

def get_traffic_packet():
    """领取流量包
    """    
    url = f'https://cvm.dogyun.com/traffic/package/level'
    headers = {
        'X-Csrf-Token': config.DOGYUN_CSRF_TOKEN,
        'Origin': 'https://cvm.dogyun.com',
        'Referer': 'https://cvm.dogyun.com/traffic/package/list',
        'Cookie': config.DOGYUN_COOKIE
    }
    # 发送post请求
    response = requests.post(url, headers=headers)
    # 获取返回的json数据
    data = response.json()
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
    bot.send_message(config.CHAT_ID, f'{current_date} {current_time} {result}')
    

def lucky_draw_notice():
    """抽奖活动通知
    """ 
    url = f'https://cvm.dogyun.com/traffic/package/list'
    pass

if __name__ == '__main__':
    
    # run
    if config.ENV == "DEV":
        bot.infinity_polling() 


    elif config.ENV == "PROD":
        import flask
        from flask import Flask, request
        
        app = flask.Flask(__name__)

        @app.route('/', methods=['GET', 'HEAD'])
        def index():
            return ""
        
        # Process webhook calls
        @app.route(WEBHOOK_URL_PATH, methods=['POST'],strict_slashes=False)
        def webhook():
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return "!", 200
        
        # 设置webhook
        bot.remove_webhook()
        # Set webhook
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
        
        scheduler = BlockingScheduler()
        # 每天尝试领一次流量包
        scheduler.add_job(get_traffic_packet, 'cron', hour='12', minute='39', args=[])
        # 每天定时监测是否有抽奖活动
        scheduler.add_job(lucky_draw_notice, 'cron', hour='2', minute='0', args=[])
        scheduler.start()
                
        # Start flask server
        app.run(host=config.WEBHOOK_LISTEN,
                port=config.WEBHOOK_PORT,
                ssl_context=(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV),
                debug=False)
        