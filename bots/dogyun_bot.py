import os
import telebot
import requests
from settings.config import dogyun_config
from datetime import datetime
from datetime import date
from bs4 import BeautifulSoup
import lxml
import subprocess

logger = telebot.logger

bot = telebot.TeleBot(dogyun_config['BOT_TOKEN'],threaded=False)

set_email_script = 'git config --global user.email "f18326186224@gmail.com"'
set_username_script = 'git config --global user.name "Jaychouzzz"'

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
    """抽奖

    Args:
        message (_type_): _description_
    """    
    url = f'https://console.dogyun.com/turntable/lottery'
    headers = {
        'X-Csrf-Token': dogyun_config['DOGYUN_CSRF_TOKEN'],
        'Origin': 'https://cvm.dogyun.com',
        'Referer': 'https://console.dogyun.com/turntable',
        'Cookie': dogyun_config['DOGYUN_COOKIE']
    }
    # 发送put请求
    try:
        response = requests.put(url, headers=headers,verify=True)
    except Exception as e:
        bot.reply_to(message, f'抽奖失败: {e.args[0]}')
        return
    # 获取返回的json数据
    try:
        data = response.json()
    except:
        # tg通知dogyun cookie已过期
        bot.reply_to(message, 'dogyun cookie已过期,请更新cookie')
        return
    # 获取抽奖结果
    result = data['success']
    if result:
        # 查看奖品
        prize_url = f'https://console.dogyun.com/turntable/prize/page'
        prize_body = {"draw":2,"columns":[{"data":"prizeName","name":"","searchable":True,"orderable":False,"search":{"value":"","regex":False}},
                                          {"data":"status","name":"","searchable":True,"orderable":False,"search":{"value":"","regex":False}},
                                          {"data":"createTime","name":"","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                                          {"data":"descr","name":"","searchable":True,"orderable":False,"search":{"value":"","regex":False}}]
                                          ,"order":[{"column":2,"dir":"desc"}],"start":0,"length":10,"search":{"value":"","regex":False}}
        # post请求
        try:
            prize_response = requests.post(prize_url,json = prize_body ,headers=headers,verify=True)
        except Exception as e:
            bot.reply_to(message, f'查看奖品失败: {e.args[0]}')
            return
        # 获取返回的json数据
        try:
            prize_data = prize_response.json()
        except:
            # tg通知dogyun cookie已过期
            bot.reply_to(message, 'dogyun cookie已过期,请更新cookie')
            return
        # 获取奖品信息
        prize_infos:list = prize_data['data']
        
        if len(prize_infos) > 0 and prize_infos[0]['createTime'].split(' ')[0] == date.today().strftime("%Y-%m-%d"):
            bot.reply_to(message, f'抽奖结果: 成功\n奖品: {prize_infos[0]["prizeName"]}\n状态: {prize_infos[0]["status"]}\n描述: {prize_infos[0]["descr"]}')
    else:
        bot.reply_to(message, f'抽奖失败: {data["message"]}')
        
@bot.message_handler(commands=['update_xray_route'])
def update_xray_route(message):
    """更新xray客户端路由规则

    Args:
        message (_type_): _description_
    """    
    script = 'curl -s https://raw.githubusercontent.com/nichuanfang/domestic-rules-generator/main/crontab.sh | bash'
    try:
        subprocess.call(f'{set_email_script}', shell=True)
        subprocess.call(f'{set_username_script}', shell=True)
        subprocess.call(script, shell=True) 
        bot.reply_to(message, '更新xray客户端路由规则成功')
    except:
        bot.reply_to(message, '更新xray客户端路由规则失败')
        
@bot.message_handler(commands=['bitwarden_backup'])
def bitwarden_backup(message):
    """备份bitwarden

    Args:
        message (_type_): _description_
    """    
    script = 'curl -s https://raw.githubusercontent.com/nichuanfang/config-server/master/linux/bash/step2/vps/backup_bitwarden.sh | bash'
    try:
        subprocess.call(f'{set_email_script}', shell=True)
        subprocess.call(f'{set_username_script}', shell=True)
        subprocess.call(script, shell=True)
        bot.reply_to(message, '备份bitwarden成功')
    except:
        bot.reply_to(message, '备份bitwarden失败')


# 每月7号
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
        bot.send_message(dogyun_config['CHAT_ID'], '抽奖活动通知失败!')
        return
    try:
        data = response.json()
    except:
        # tg通知dogyun cookie已过期
        bot.send_message(dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie!')
        return
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        result = soup.find('a',class_='gb-turntable-btn').text
        bot.send_message(dogyun_config['CHAT_ID'], f'抽奖活动通知: {soup.find("strong").text}')
        logger.info(f'抽奖活动通知: {soup.find("strong").text}')
    except:
        # '暂无抽奖活动'
        pass