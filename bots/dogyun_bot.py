import re
import telebot
import requests
from settings.config import dogyun_config, github_config
from datetime import datetime
from datetime import date
from bs4 import BeautifulSoup
import lxml
import subprocess
import json

logger = telebot.logger

bot = telebot.TeleBot(dogyun_config['BOT_TOKEN'], threaded=False)


@bot.message_handler(commands=['server_info'])
def get_server_status(message):
    """获取服务器状态

    Returns:
        _type_: _description_
    """
    url = f'https://vm.dogyun.com/server/{dogyun_config["DOGYUN_SERVER_ID"]}'
    headers = {
        'X-Csrf-Token': dogyun_config['DOGYUN_CSRF_TOKEN'],
        'Origin': 'https://cvm.dogyun.com',
        'Referer': 'https://cvm.dogyun.com',
        'Cookie': dogyun_config['DOGYUN_COOKIE']
    }
    try:
        # 发送post请求
        response = requests.get(url, headers=headers, verify=True)
        if response.url == 'https://account.dogyun.com/login':
            # tg通知dogyun cookie已过期
            bot.send_message(
                dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie! \n https://github.com/nichuanfang/tgbot/edit/main/settings/config.py')
            return
    except Exception as e:
        logger.error(e)
        return
    soup = BeautifulSoup(response.text, 'lxml')
    # cpu
    cpu = soup.find_all(
        'div', class_='d-flex justify-content-between')[0].contents[1].contents[0]
    # 内存
    mem = soup.find_all(
        'div', class_='d-flex justify-content-between')[1].contents[1].next
    # 本日流量
    curr_day_throughput = soup.find('span', class_='text-primary').text
    # 剩余流量
    rest_throughput = str(float(soup.find_all(
        'div', class_='d-flex justify-content-between')[2].contents[3].next.split('/')[1].split(' ')[1]) - float(soup.find_all(
            'div', class_='d-flex justify-content-between')[2].contents[3].next.split('/')[0].split(' ')[0])) + ' GB'
    # 重置时间
    reset_time = soup.find_all('div', class_='d-flex justify-content-between')[
        2].contents[1].contents[1].text.split(' ')[0]

    status_message = f'CPU: {cpu}\n内存: {mem}\n本日流量: {curr_day_throughput}\n剩余流量: {rest_throughput}\n重置时间: {reset_time}'
    bot.reply_to(message, status_message)


@bot.message_handler(commands=['update_cookie'])
def update_cookie(message):
    # 更新cookie
    dogyun_cookie = message.text[14:].strip()
    if len(dogyun_cookie) != 48:
        bot.reply_to(message, 'cookie格式错误')
        return

    # 更新tgbot的dogyun cookie
    tgbot_token = 'ZG9neXVuX2NvbmZpZyA9IHsKICAgICMgdGfphY3nva4KICAgICdCT1RfVE9LRU4nOiAnNjUyMDc2NjkxNzpBQUY2RlVUd3pwUFlhMGYwanEzTEFWVDhuUnplNHhIMEY3dycsCiAgICAnQ0hBVF9JRCc6IDU5MTM1NjUzMDAsCiAgICAjIGRvZ3l1buebuOWFswogICAgJ0RPR1lVTl9BUElfS0VZJzogJ0NYNzVBS0lKT0dRWTNKVUdHNURKRjNSTVFYMEtWME9SVDVQTCcsCiAgICAnRE9HWVVOX1NFUlZFUl9JRCc6ICc0MDE3OScsCiAgICAnRE9HWVVOX0NTUkZfVE9LRU4nOiAnNTY2Y2ZiNTItYTA0YS00YTczLWFlZDYtODM1YjAzNWM3MDg3JywKICAgICdET0dZVU5fQ09PS0lFJzogJ1NFU1NJT049T1RZM1ptUmpNelF0TW1GaU1pMDBaamRpTFdJMllqUXRaV001TVRCaU9Ua3hZVE0yJwp9CgpnaXRodWJfY29uZmlnID0gewogICAgJ0JPVF9UT0tFTic6ICc2NDUyNDk5MjkxOkFBRktDZG5XbnJVbmppMXZkc0txSDdxNFBEdkFOUHNvQWVRJywKICAgICdDSEFUX0lEJzogNTkxMzU2NTMwMCwKICAgICdHSVRIVUJfVE9LRU4nOiAnZ2hwX1UyTUhzNnRoeVNQdnB3Z1BsREZua09iOVhFRTM3YjFXTHhvSScsCn0KCnRtZGJfY29uZmlnID0gewogICAgJ0JPVF9UT0tFTic6ICc2MzMxMTA4OTc0OkFBRkwyMUl0TWJTX3UxRmxlYVltQnhPUTNSWVVUMzA2Skk0JywKICAgICdDSEFUX0lEJzogNTkxMzU2NTMwMCwKICAgICdBUElfS0VZJzogJ2MwZjY5YWFhYTNiNmNiZjU3Y2E3MjUxNjljNzdmMjE5Jwp9Cgp0cmFpbl9jb25maWcgPSB7CiAgICAnQk9UX1RPS0VOJzogJzY1ODk0NDUwMDc6QUFGa3lvTlgtLXlGODJkWEc4Q1JwSU4yWC1naFozLWRJNXcnLAogICAgJ0NIQVRfSUQnOiA1OTEzNTY1MzAwLAp9Cgp2cHNfY29uZmlnID0gewogICAgJ1ZQU19IT1NUJzogJzE0OS4xMDQuMjIuMjUxJywKICAgICdWUFNfUE9SVCc6IDYwNDU2LAogICAgJ1ZQU19VU0VSJzogJ3Jvb3QnLAogICAgJ1ZQU19QQVNTV09SRCc6ICdOOU5YaU9wczdMUmknLAp9Cg=='

    header = {
        'Accept': 'application/vnd.github.everest-preview+json',
        'Authorization': f'token {github_config["GITHUB_TOKEN"]}'
    }
    requests.post('https://api.github.com/repos/nichuanfang/tgbot/dispatches',
                  data=json.dumps({"event_type": "update_cookie", "client_payload": {"tgbot_token": f"{tgbot_token}"}}), headers=header)
    bot.reply_to(message, '已触发工作流: 更新cookie')


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
        response = requests.post(url, headers=headers, verify=True)
        if response.url == 'https://account.dogyun.com/login':
            # tg通知dogyun cookie已过期
            bot.send_message(
                dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie! \n https://github.com/nichuanfang/tgbot/edit/main/settings/config.py')
            return
        data = response.json()
    except Exception as e:
        logger.error(e)
        return
    # 获取领取结果
    result = data['message']
    bot.reply_to(message, result)


@bot.message_handler(commands=['query_package'])
def query_package(message):
    """查询流量包
    """
    url = f'https://cvm.dogyun.com/traffic/package/page'
    headers = {
        'X-Csrf-Token': dogyun_config['DOGYUN_CSRF_TOKEN'],
        'Origin': 'https://cvm.dogyun.com',
        'Referer': 'https://cvm.dogyun.com/traffic/package/list',
        'Cookie': dogyun_config['DOGYUN_COOKIE']
    }

    body = {
        'query[status]': 'available',
        'pagination[page]': 1,
        'pagination[pages]': 1,
        'pagination[perpage]': 10,
        'pagination[total]': 1,
        'sort[sort]': 'desc',
        'sort[field]': 'expireTime'
    }
    try:
        # 发送post请求
        response = requests.post(url, headers=headers,
                                 data=body, verify=True)
        if response.url == 'https://account.dogyun.com/login':
            # tg通知dogyun cookie已过期
            bot.send_message(
                dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie! \n')
        data = response.json()
    except:
        bot.reply_to(message, '查询流量包失败')
        return
    if 'data' in data:
        packages: list = data['data']
        package_text = ''
        for index, package in enumerate(packages):
            package_text = f'•流量包{index+1}:\n'
            package_text += f'  类型: {package["type"]}\n'
            package_text += f'  总计: {package["total"]}\n'
            package_text += f'  剩余: {package["surplus"]}\n'
            package_text += f'  过期时间: {package["expireTime"]}\n\n'
        bot.reply_to(message, package_text)


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
        response = requests.put(url, headers=headers, verify=True)
        if response.url == 'https://account.dogyun.com/login':
            # tg通知dogyun cookie已过期
            bot.send_message(
                dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie! \n https://github.com/nichuanfang/tgbot/edit/main/settings/config.py')
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
        prize_body = {"draw": 2, "columns": [{"data": "prizeName", "name": "", "searchable": True, "orderable": False, "search": {"value": "", "regex": False}},
                                             {"data": "status", "name": "", "searchable": True, "orderable": False, "search": {
                                                 "value": "", "regex": False}},
                                             {"data": "createTime", "name": "", "searchable": True, "orderable": True, "search": {
                                                 "value": "", "regex": False}},
                                             {"data": "descr", "name": "", "searchable": True, "orderable": False, "search": {"value": "", "regex": False}}], "order": [{"column": 2, "dir": "desc"}], "start": 0, "length": 10, "search": {"value": "", "regex": False}}
        # post请求
        try:
            prize_response = requests.post(
                prize_url, json=prize_body, headers=headers, verify=True)
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
        prize_infos: list = prize_data['data']

        if len(prize_infos) > 0 and prize_infos[0]['createTime'].split(' ')[0] == date.today().strftime("%Y-%m-%d"):
            bot.reply_to(
                message, f'抽奖结果: 成功\n奖品: {prize_infos[0]["prizeName"]}\n状态: {prize_infos[0]["status"]}\n描述: {prize_infos[0]["descr"]}')
    else:
        bot.reply_to(message, f'抽奖失败: {data["message"]}')


@bot.message_handler(commands=['bitwarden_backup'])
def bitwarden_backup(message):
    """备份bitwarden

    Args:
        message (_type_): _description_
    """
    script = 'curl -s https://raw.githubusercontent.com/nichuanfang/config-server/master/linux/bash/step2/vps/backup_bitwarden.sh | bash'
    # try:
    #     ssd_fd = ssh_connect(vps_config["VPS_HOST"], vps_config["VPS_PORT"],
    #                          vps_config["VPS_USER"], vps_config["VPS_PASS"])
    # except:
    #     bot.reply_to(message, f'无法连接到服务器{vps_config["VPS_HOST"]}')
    #     return
    try:
        subprocess.call(
            f'nsenter -m -u -i -n -p -t 1 bash -c "{script}"', shell=True)
    except:
        bot.reply_to(message, '执行脚本报错')
        return
    bot.reply_to(message, '备份bitwarden成功')


@bot.message_handler(commands=['exec_cmd'])
def exec_cmd(message):
    """执行bash脚本

    Args:
        message (_type_): _description_
    """
    script = message.text[10:]
    if script in ['systemctl stop tgbot', 'systemctl restart tgbot', 'reboot']:
        bot.reply_to(message, '禁止执行该命令')
        return
    # try:
    #     ssd_fd = ssh_connect(vps_config["VPS_HOST"], vps_config["VPS_PORT"],
    #                          vps_config["VPS_USER"], vps_config["VPS_PASS"])
    # except:
    #     bot.reply_to(message, f'无法连接到服务器{vps_config["VPS_HOST"]}')
    #     return
    try:
        subprocess.call(
            f'nsenter -m -u -i -n -p -t 1 bash -c "{script}"', shell=True)
    except:
        bot.reply_to(message, '执行命令报错')
        return
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
        response = requests.post(url, headers=headers, verify=True)
        if response.url == 'https://account.dogyun.com/login':
            # tg通知dogyun cookie已过期
            bot.send_message(
                dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie! \n https://github.com/nichuanfang/tgbot/edit/main/settings/config.py')
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
        response = requests.get(url, headers=headers, verify=True)
        if response.url == 'https://account.dogyun.com/login':
            # tg通知dogyun cookie已过期
            bot.send_message(
                dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie! \n https://github.com/nichuanfang/tgbot/edit/main/settings/config.py')
            return
    except Exception as e:
        logger.error(e)
        return
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        result = soup.find('a', class_='gb-turntable-btn').text
        bot.send_message(dogyun_config['CHAT_ID'],
                         f'抽奖活动通知: {soup.find("strong").text}')
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
        response = requests.get(url, headers=headers, verify=True)
        if response.url == 'https://account.dogyun.com/login':
            # tg通知dogyun cookie已过期
            bot.send_message(
                dogyun_config['CHAT_ID'], 'dogyun cookie已过期,请更新cookie! \n https://github.com/nichuanfang/tgbot/edit/main/settings/config.py')
            return
    except Exception as e:
        logger.error(e)
        return
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        result = soup.find('span', class_='h5 font-weight-normal').text
        # 根据正则表达式提取数字
        balance = re.findall(r"\d+\.?\d*", result)[0]
        if float(balance) < 10:
            bot.send_message(dogyun_config['CHAT_ID'], f'余额不足提醒: {balance}元')
            logger.info(f'余额不足提醒: {balance}元')
    except:
        pass
