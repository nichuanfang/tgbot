import os
import re
import telebot
import requests
from settings.config import dogyun_config
from datetime import datetime
from datetime import date
from bs4 import BeautifulSoup
import lxml
import paramiko

logger = telebot.logger

bot = telebot.TeleBot(dogyun_config['BOT_TOKEN'],threaded=False)


# 连接方法
def ssh_connect( _host,_port,_username, _password ):
    try:
        _ssh_fd = paramiko.SSHClient()
        _ssh_fd.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
        _ssh_fd.connect( _host, port=_port ,username = _username, password = _password )
    except Exception as e:
        print( 'ssh %s@%s: %s' % (_username, _host, e) )
        exit()
    return _ssh_fd

# 运行命令
def ssh_exec_cmd( _ssh_fd, _cmd):
    stdin, stdout, stderr =  _ssh_fd.exec_command( _cmd )
    while not stdout.channel.exit_status_ready():
        result = stdout.readline()
        if stdout.channel.exit_status_ready():
            a = stdout.readlines()
            logger.info(a)
            return

# 关闭SSH
def ssh_close( _ssh_fd ):
    _ssh_fd.close()
    

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
        if response.url == 'https://account.dogyun.com/login':
            # tg通知dogyun cookie已过期
            bot.send_message(dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie!')
            return
        data = response.json()
    except Exception as e:
        logger.error(e)
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
        if response.url == 'https://account.dogyun.com/login':
            # tg通知dogyun cookie已过期
            bot.send_message(dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie!')
            return
        data = response.json()
    except Exception as e:
        logger.error(e)
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
        ssd_fd = ssh_connect('154.202.60.190',60022,'root','Ld08MAiSoL8Ag9P')
    except:
        bot.reply_to(message, '无法连接到服务器154.202.60.190')
        return
    try:
        ssh_exec_cmd(ssd_fd,script)
    except:
        bot.reply_to(message, '执行脚本报错')
        return
    ssh_close(ssd_fd)
    bot.reply_to(message, '更新xray客户端路由规则成功')
        
@bot.message_handler(commands=['bitwarden_backup'])
def bitwarden_backup(message):
    """备份bitwarden

    Args:
        message (_type_): _description_
    """    
    script = 'curl -s https://raw.githubusercontent.com/nichuanfang/config-server/master/linux/bash/step2/vps/backup_bitwarden.sh | bash'
    try:
        ssd_fd = ssh_connect('154.202.60.190',60022,'root','Ld08MAiSoL8Ag9P')
    except:
        bot.reply_to(message, '无法连接到服务器154.202.60.190')
        return
    try:
        ssh_exec_cmd(ssd_fd,script)
    except:
        bot.reply_to(message, '执行脚本报错')
        return
    ssh_close(ssd_fd)
    bot.reply_to(message, '备份bitwarden成功')

# 执行bash脚本
@bot.message_handler(commands=['exec_cmd'])
def exec_cmd(message):
    """执行bash脚本

    Args:
        message (_type_): _description_
    """    
    script = message.text[10:]
    if script in ['systemctl stop tgbot','systemctl restart tgbot','reboot']:
        bot.reply_to(message, '禁止执行该命令')
        return
    try:
        ssd_fd = ssh_connect('154.202.60.190',60022,'root','Ld08MAiSoL8Ag9P')
    except:
        bot.reply_to(message, '无法连接到服务器154.202.60.190')
        return
    try:
        ssh_exec_cmd(ssd_fd,script)
    except:
        bot.reply_to(message, '执行命令报错')
        return
    ssh_close(ssd_fd)
    bot.reply_to(message, '执行命令成功')


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
        if response.url == 'https://account.dogyun.com/login':
            # tg通知dogyun cookie已过期
            bot.send_message(dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie!')
            return
        data = response.json()
    except Exception as e:
        logger.error(e)
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
        if response.url == 'https://account.dogyun.com/login':
            # tg通知dogyun cookie已过期
            bot.send_message(dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie!')
            return
        data = response.json()
    except Exception as e:
        logger.error(e)
        return
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        result = soup.find('a',class_='gb-turntable-btn').text
        bot.send_message(dogyun_config['CHAT_ID'], f'抽奖活动通知: {soup.find("strong").text}')
        logger.info(f'抽奖活动通知: {soup.find("strong").text}')
    except:
        # '暂无抽奖活动'
        pass
    
    
# 余额不足提醒
def balance_lack_notice():
    """余额不足提醒
    """ 
    url = f'https://console.dogyun.com'
    headers = {
        'Cookie': dogyun_config['DOGYUN_COOKIE'],
        'Referer': 'https://member.dogyun.com/',
        'Origin': 'https://console.dogyun.com',
        'X-Csrf-Token': dogyun_config['DOGYUN_CSRF_TOKEN']
    }
    try:
        # 发起get请求
        response = requests.get(url, headers=headers,verify=True)
        if response.url == 'https://account.dogyun.com/login':
            # tg通知dogyun cookie已过期
            bot.send_message(dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie!')
            return
    except Exception as e:
        logger.error(e)
        return
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        result = soup.find('span',class_='h5 font-weight-normal').text
        # 根据正则表达式提取数字
        balance = re.findall(r"\d+\.?\d*", result)[0]
        if float(balance) < 100:
            bot.send_message(dogyun_config['CHAT_ID'], f'余额不足提醒: {balance}元')
            logger.info(f'余额不足提醒: {balance}元')
    except:
        pass
    
@bot.message_handler(content_types=['text'])
def common(message):
    raw_msg = message.text.strip().replace(' ', '')
    # 更新cookie
    if raw_msg and not raw_msg.startswith('/') and raw_msg.startswith('SESSION=') and len(raw_msg)==len(dogyun_config['DOGYUN_COOKIE']):
        # 提交到github
        with open('/root/code/tgbot/settings/config.py', 'r+',encoding='utf-8') as f:
            lines = f.readlines()
        with open('/root/code/tgbot/settings/config.py', 'w+',encoding='utf-8') as f:
            for line in lines:
                if line.lstrip().startswith('\'DOGYUN_COOKIE\''):
                    line = f'    \'DOGYUN_COOKIE\' : \'{raw_msg}\'\n'
                f.write(line)
        # 提交到github
        os.system('cd /root/code/tgbot')
        os.system('git add /root/code/tgbot/settings/config.py')
        os.system('git commit -m "update dogyun cookie"')
        os.system('git push')   
        bot.reply_to(message, '更新cookie成功')
        return