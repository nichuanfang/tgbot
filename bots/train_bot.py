import datetime
import json
import re
from time import sleep
import requests
import telebot
from settings.config import train_config
import fake_useragent
from rich.console import Console
from rich import print
import traceback

# =====================全局变量==================================
ua = fake_useragent.UserAgent()

logger = telebot.logger

console = Console()

# 通用请求头
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7,ja;q=0.6',
    # 每次请求ua重新构造
    # 'User-Agent': ua.chrome,
    'Host': 'kyfw.12306.cn',
    'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    # 每次请求cookie的_jc_save_toDate重新构造 否则报错
    # 'Cookie': '_jc_save_toDate=2023-10-17',
    'If-Modified-Since': '0',
    'Sec-Ch-Ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'X-Requested-With': 'XMLHttpRequest'
}
# 余票查询接口
url: str = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'
# 票价查询接口
train_price_url = 'https://kyfw.12306.cn/otn/leftTicketPrice/queryAllPublicPrice?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}'
# 车次详情接口
train_info_url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no={}&from_station_telecode={}&to_station_telecode={}&depart_date={}'
# =============================类===========================================


class Train:

    def __init__(self,
                 train_code: str,
                 train_no: str,
                 from_station: str,
                 to_station: str,
                 date: str,
                 start_time: str,
                 arrive_time: str,
                 duration: str,
                 no_seat: str,
                 second_seat: str,
                 first_seat: str,
                 special_seat: str,
                 hard_seat: str,
                 hard_sleep_seat: str,
                 soft_sleep_seat: str
                 ) -> None:
        """车次对象

        Args:
            train_code (str): 车次编码
            train_no (str): 车次号
            from_station (str): 起点站
            to_station (str): 终点站
            date (str): 日期信息
            start_time (str): 发车时间
            arrive_time (str): 到站时间
            duration (str): 历时
            no_seat (str): 无座
            -------------------------
            second_seat (str): 二等座
            first_seat (str): 一等座
            special_seat (str): 特等座
            ---------------------------
            hard_seat (str): 硬座
            hard_sleep_seat (str): 硬卧
            soft_sleep_seat (str): 软卧
        """
        self.train_code = train_code
        self.train_no = train_no
        self.start_station_name = ''
        self.end_station_name = ''
        self.from_station = from_station
        self.to_station = to_station
        self.date = date
        self.start_time = start_time
        self.arrive_time = arrive_time
        self.duration = duration
        self.no_seat = no_seat
        self.second_seat = second_seat
        self.first_seat = first_seat
        self.special_seat = special_seat
        self.hard_seat = hard_seat
        self.hard_sleep_seat = hard_sleep_seat
        self.soft_sleep_seat = soft_sleep_seat
# =================================业务处理方法=============================================


def load_stations():
    """获取站点信息

    Returns:
        _type_: _description_
    """
    # /root/code/tgbot/
    with open('/root/code/tgbot/stations.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def update_station(url: str):
    """更新站点信息

    Returns:
        _type_: _description_
    """
    if url == None or url == '':
        url = 'https://www.12306.cn/index/script/core/common/station_name_new_v10018.js'
    requests.packages.urllib3.disable_warnings()
    response = requests.get(url, verify=False)
    stations = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)', response.text)
    stations = dict(stations)
    # 保存为文件
    with open('stations.json', 'w', encoding='utf-8') as f:
        json.dump(stations, f, ensure_ascii=False)
    return stations


def decrypt(string):
    """解密车次信息

    Args:
        string (_type_): 加密串

    Returns:
        _type_: _description_
    """
    res = {}
    string = ''.join(string)
    split_list = string.split('|')
    try:
        res['train_code'] = split_list[2]
        res['train_no'] = split_list[3]
        res['from_station'] = split_list[6]
        res['to_station'] = split_list[7]
        res['date'] = split_list[13]
        res['start_time'] = split_list[8]
        res['arrive_time'] = split_list[9]
        res['duration'] = split_list[10]
        res['no_seat'] = split_list[26]
        res['second_seat'] = split_list[30]
        res['first_seat'] = split_list[31]
        res['special_seat'] = split_list[32]
        res['hard_seat'] = split_list[29]
        res['hard_sleep_seat'] = split_list[28]
        res['soft_sleep_seat'] = split_list[23]
        return Train(**res)
    except Exception as e:
        traceback.print_exc()
        return None


def has_seat(train: Train):
    """判断该车次是否有座位 如果车次规定了发车时间 则判断是否在发车时间之后

    Args:
        train (Train): _description_

    Returns:
        _type_: _description_
    """
    if train.train_code[0] != 'G' and train.train_code[0] != 'D' and train.train_code[0] != 'C':
        # 如果是火车
        if (train.no_seat != '无' and train.no_seat != '') |\
            (train.hard_seat != '无' and train.hard_seat != '') |\
            (train.hard_sleep_seat != '无' and train.hard_sleep_seat != '') |\
                (train.soft_sleep_seat != '无' and train.soft_sleep_seat != ''):
            return True
        return False
    else:
        # 如果是动车
        if (train.no_seat != '无' and train.no_seat != '') |\
            (train.second_seat != '无' and train.second_seat != '') |\
            (train.first_seat != '无' and train.first_seat != '') |\
                (train.special_seat != '无' and train.special_seat != ''):
            return True
        return False


def query_train_info(train_code: str, from_station_code, to_station_code, date: str):
    """根据车次编码查询车次信息

    Args:
        message (_type_): 车次编码
    """
    request_url = train_info_url.format(
        train_code, from_station_code, to_station_code, date)
    headers['User-Agent'] = ua.chrome
    headers['Cookie'] = f'_jc_save_toDate={date}'
    response = requests.get(request_url, headers=headers)
    if response.status_code != 200:
        return None
    sleep(0.5)
    return json.loads(response.text)['data']['data']

# 查询车次价格


def query_train_price(train_date: str, from_station_code, to_station_code):
    """根据车次编码查询车次信息

    Args:
        message (_type_): 车次编码
    """
    request_url = train_price_url.format(
        train_date, from_station_code, to_station_code)
    headers['User-Agent'] = ua.chrome
    headers['Cookie'] = f'_jc_save_toDate={train_date}'
    response = requests.get(request_url, headers=headers)
    if response.status_code != 200:
        return None
    sleep(0.5)
    return json.loads(response.text)['data']


def second_or_no_seat_nums(collect_trains: list[Train]):
    # 计算二等座或无座有票的车次总数
    count = 0
    for train in collect_trains:
        if (train.second_seat != '无' and train.second_seat != '') or (train.no_seat != '无' and train.no_seat != ''):
            count += 1
    return count


def handle(message, stations: dict, result: list[Train], train_time):
    """处理查询结果

    Args:
        result (list[list[str]]): _description_
    """
    reversed_stations = {v: k for k, v in stations.items()}
    collect_trains = []
    # 买长的终点站
    long_buy_trains = {}
    for train in result:
        # 如果二等座或无座有票的车次总数大于10 停止查询
        if second_or_no_seat_nums(collect_trains) >= 10:
            break
        # 如果发车时间不为空 则判断是否在发车时间之后
        if train_time != '':
            # 字符串转日期对象
            time1 = datetime.datetime.strptime(
                train.start_time+':00', '%H:%M:%S')
            time2 = datetime.datetime.strptime(
                train_time, '%H:%M:%S')
            if time1 < time2:
                continue
        else:
            # 如果离火车开点不足半小时 跳过
            time1 = datetime.datetime.strptime(
                train.start_time+':00', '%H:%M:%S')
            time2 = datetime.datetime.now()
            if (time1 - time2).seconds < 1800:
                continue
        # 查询车次号
        try:
            raw_date = f'{train.date[0:4]}-{train.date[4:6]}-{train.date[6:8]}'
            train_info: list[dict] = query_train_info(
                train.train_code, train.from_station, train.to_station, raw_date)
        except Exception as e:
            traceback.print_exc()
            if has_seat(train):
                collect_trains.append(train)
            continue
        if has_seat(train):
            train.start_station_name = train_info[0]['start_station_name']
            train.end_station_name = train_info[0]['end_station_name']
            train.train_no = train_info[0]['station_train_code']
            collect_trains.append(train)
        # 以from_station为起点 逐个站点查找 至到to_station
        station_from_flag = False
        station_to_flag = False
        station_index = 0
        train_info_long_buys = []
        for train_info_item in train_info:
            to_station = train_info_item['station_name']
            if station_from_flag:
                # 买短补长和买长扣短相结合
                if stations[to_station] == train.to_station:
                    station_to_flag = True
                    station_index += 1
                    continue
                # 允许往后跳两站
                if station_index > 2:
                    break
                # 业务逻辑...
                # -------------------------------------------------
                console.log(
                    f'[{train.train_no}]正在查询{reversed_stations[train.from_station]}到{to_station}的车次...')
                headers['Cookie'] = f'_jc_save_toDate={train.date}'
                max_retries = 3
                while True:
                    try:
                        if max_retries <= 0:
                            bot.send_message(message.chat.id, '查询失败: 重试次数过多')
                            return None
                        headers['User-Agent'] = ua.chrome
                        train_request_url = url.format(
                            raw_date, train.from_station, stations[to_station])
                        response = requests.get(
                            train_request_url, headers=headers)
                        if response.status_code != 200:
                            bot.send_message(message.chat.id, '查询失败')
                            return None
                        break
                    except Exception as e:
                        bot.send_message(
                            message.chat.id, f'查询失败: 第{3-max_retries+1}次重试中')
                        traceback.print_exc()
                        max_retries -= 1
                if response.status_code != 200:
                    continue
                try:
                    train_info_json_data = json.loads(response.text)
                    train_info_item_result = train_info_json_data['data']['result']
                    train_info_new_result = [decrypt(item)
                                             for item in train_info_item_result]
                    # 过滤出train_info_new_result中train_code=train.train_code的车次
                    train_info_new_result = list(
                        filter(lambda x: x.train_code == train.train_code, train_info_new_result))
                    if train_info_new_result == None or len(train_info_new_result) == 0:
                        continue
                    if has_seat(train_info_new_result[0]):
                        if station_index > 0:
                            train_info_long_buys.append(
                                train_info_new_result[0].to_station)
                        # 更新车次号
                        train_info_new_result[0].train_no = train_info[0]['station_train_code']
                        train_info_new_result[0].start_station_name = train_info[0]['start_station_name']
                        train_info_new_result[0].end_station_name = train_info[0]['end_station_name']
                        collect_trains.append(train_info_new_result[0])
                    # 防止请求过于频繁
                    sleep(0.5)
                    # handle(message, stations, new_result)
                except Exception as e:
                    traceback.print_exc()
                    continue
                if station_to_flag:
                    station_index += 1
                # -------------------------------------------------------------------------------------
            else:
                if stations[to_station] == train.from_station:
                    station_from_flag = True
                continue
        if len(train_info_long_buys) > 0:
            long_buy_trains[train.train_code] = train_info_long_buys
        sleep(0.5)
    return (collect_trains, reversed_stations, long_buy_trains)

# ================================telegram bot======================================


bot = telebot.TeleBot(train_config['BOT_TOKEN'], threaded=False)


@bot.message_handler(commands=['readme'])
def query_left_ticket(message):
    text = '[注]:\n\n1. 余票格式【无座|二等座|一等座|特等座】【无座|硬座|硬卧|软卧】\n2. 出发站/到站格式【起点|上车点】【终点|下车点】'
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['query_left_ticket'])
def query_left_ticket(message):
    text = '请输入起始站'
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent_msg, from_station_handler)


def from_station_handler(message):
    from_station = message.text
    # 判断是否在stations中
    stations = load_stations()
    if from_station not in stations.keys():
        text = '站点不存在,请重新输入'
        sent_msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(sent_msg, from_station_handler)
        return None

    text = '请输入目的站'
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(
        sent_msg, to_station_handler, stations, from_station)


def to_station_handler(message, stations, from_station):
    to_station = message.text
    # 判断是否在stations中
    if to_station not in stations.keys():
        text = '站点不存在,请重新输入'
        sent_msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(
            sent_msg, to_station_handler, stations, from_station)
        return None

    text = '请输入出发日期,时分秒可省略.\n格式: 【yyyy-MM-dd HH:mm:ss】'
    sent_msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(
        sent_msg, query_handler, stations, from_station, to_station)


def get_price_dict(prices):
    prices_dict = {}
    for price in prices:
        try:
            no_seat_price = price['queryLeftNewDTO']['ze_price']
            # 00320转换为价格
            no_seat_price = str(float(no_seat_price) / 10)
        except:
            no_seat_price = None
        try:
            second_price = price['queryLeftNewDTO']['ze_price']
            second_price = str(float(second_price) / 10)
        except:
            second_price = None
        try:
            first_price = price['queryLeftNewDTO']['zy_price']
            first_price = str(float(first_price) / 10)
        except:
            first_price = None
        try:
            special_price = price['queryLeftNewDTO']['swz_price']
            special_price = str(float(special_price) / 10)
        except:
            special_price = None

        prices_dict[price['queryLeftNewDTO']['train_no']] = {
            'no_seat': no_seat_price,
            'second_seat': second_price,
            'first_seat': first_price,
            'special_seat': special_price
        }
    return prices_dict


def assemble_bot_msg(to_station, train: Train, stations, reversed_stations, prices_dict, long_buy: bool):
    train_message = ''
    # 判断是否是火车
    if train.train_code[0] != 'G' and train.train_code[0] != 'D' and train.train_code[0] != 'C':
        # 火车
        train_message = train_message + f'•  车次:  【{train.train_no}】\n'
        train_message = train_message + \
            f'    出发站:  {train.start_station_name}|{reversed_stations[train.from_station]}\n'
        train_message = train_message + \
            f'    到达站:  {train.end_station_name}|{reversed_stations[train.to_station]}\n'
        train_message = train_message + \
            f'    出发时间:  {train.start_time}\n'
        train_message = train_message + \
            f'    到达时间:  {train.arrive_time}\n'
        # 无座|硬座|硬卧|软卧
        train_message = train_message + \
            f'    座位:  无座|硬座|硬卧|软卧\n'
        train_message = train_message + \
            f'    余票:  {"无" if  train.no_seat== "" else train.no_seat}|{"无" if train.hard_seat == "" else train.hard_seat}|{"无" if train.hard_sleep_seat=="" else train.hard_sleep_seat}|{"无" if train.soft_sleep_seat=="" else train.soft_sleep_seat}\n'
        # 价格
        try:
            if train.to_station == stations[to_station] or long_buy:
                train_message = train_message + \
                    f'    价格:  {"无" if prices_dict[train.train_code]["no_seat"] == None else prices_dict[train.train_code]["no_seat"]}|{"无" if prices_dict[train.train_code]["second_seat"] == None else prices_dict[train.train_code]["second_seat"]}|{"无" if prices_dict[train.train_code]["first_seat"] == None else prices_dict[train.train_code]["first_seat"]}|{"无" if prices_dict[train.train_code]["special_seat"] == None else prices_dict[train.train_code]["special_seat"]}\n'
            else:
                # 补票加两元
                train_message = train_message + \
                    f'    价格:  {"无" if prices_dict[train.train_code]["no_seat"] == None else str(float(prices_dict[train.train_code]["no_seat"]) + 2)}|{"无" if prices_dict[train.train_code]["second_seat"] == None else str(float(prices_dict[train.train_code]["second_seat"]) + 2)}|{"无" if prices_dict[train.train_code]["first_seat"] == None else str(float(prices_dict[train.train_code]["first_seat"]) + 2)}|{"无" if prices_dict[train.train_code]["special_seat"] == None else str(float(prices_dict[train.train_code]["special_seat"]) + 2)}\n'
        except:
            pass
        train_message = train_message + f'~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
    else:
        train_message = train_message + f'•  车次:  【{train.train_no}】\n'
        train_message = train_message + \
            f'    出发站:  {train.start_station_name}|{reversed_stations[train.from_station]}\n'
        train_message = train_message + \
            f'    到达站:  {train.end_station_name}|{reversed_stations[train.to_station]}\n'
        train_message = train_message + \
            f'    出发时间:  {train.start_time}\n'
        train_message = train_message + \
            f'    到达时间:  {train.arrive_time}\n'
        # 无座|二等座|一等座|商务座
        train_message = train_message + \
            f'    座位:  无座|二等座|一等座|商务座\n'
        train_message = train_message + \
            f'    余票:  {"无" if  train.no_seat== "" else train.no_seat}|{"无" if train.second_seat == "" else train.second_seat}|{"无" if train.first_seat=="" else train.first_seat}|{"无" if train.special_seat=="" else train.special_seat}\n'
        # 价格
        try:
            if train.to_station == stations[to_station] or long_buy:
                train_message = train_message + \
                    f'    价格:  {"无" if prices_dict[train.train_code]["no_seat"] == None else prices_dict[train.train_code]["no_seat"]}|{"无" if prices_dict[train.train_code]["second_seat"] == None else prices_dict[train.train_code]["second_seat"]}|{"无" if prices_dict[train.train_code]["first_seat"] == None else prices_dict[train.train_code]["first_seat"]}|{"无" if prices_dict[train.train_code]["special_seat"] == None else prices_dict[train.train_code]["special_seat"]}\n'
            else:
                # 补票加两元
                train_message = train_message + \
                    f'    价格:  {"无" if prices_dict[train.train_code]["no_seat"] == None else str(float(prices_dict[train.train_code]["no_seat"]) + 2)}|{"无" if prices_dict[train.train_code]["second_seat"] == None else str(float(prices_dict[train.train_code]["second_seat"]) + 2)}|{"无" if prices_dict[train.train_code]["first_seat"] == None else str(float(prices_dict[train.train_code]["first_seat"]) + 2)}|{"无" if prices_dict[train.train_code]["special_seat"] == None else str(float(prices_dict[train.train_code]["special_seat"]) + 2)}\n'
        except:
            pass
        train_message = train_message + f'~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
    return train_message


def query_handler(message, stations, from_station, to_station):
    date = message.text
    # 校验日期格式 时分秒可省略 yyyy-MM-dd HH:mm:ss
    # 必须完全匹配
    if not re.fullmatch(r'(\d){4}-(\d){1,2}-(\d){1,2}(\s)*((\s)+(\d){1,2}:(\d){1,2}:(\d){1,2})*', date):
        text = '日期格式错误,请重新输入'
        sent_msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(
            sent_msg, query_handler, stations, from_station, to_station)
        return None

    date = re.sub(r'\s+', ' ', date).strip()
    # 获取日期年月日部分
    train_date = date.split(' ')[0]
    # 获取日期时分秒部分

    train_time = date.split(' ')[1] if len(
        date.split(' ')) == 2 else ''

    bot.send_message(message.chat.id, '正在查询...')
    console.log(
        f'正在查询{from_station}到{to_station}的车次...')
    request_url = url.format(
        train_date, stations[from_station], stations[to_station])
    headers['User-Agent'] = ua.chrome
    headers['Cookie'] = f'_jc_save_toDate={train_date}'
    try:
        response = requests.get(request_url, headers=headers)
    except Exception as e:
        traceback.print_exc()
        bot.send_message(message.chat.id, f'查询失败:{e}')
        return None
    if response.status_code != 200:
        bot.send_message(message.chat.id, '查询失败')
        return None
    try:
        json_data = json.loads(response.text)
        result = json_data['data']['result']
        new_result = [decrypt(item) for item in result]
        collect = handle(message, stations, new_result, train_time)
        collect_result = collect[0]
        reversed_stations = collect[1]
        long_buy_trains = collect[2]
        if collect_result == None or len(collect_result) == 0:
            bot.send_message(message.chat.id, '无余票')
            return None
        bot.send_message(message.chat.id, '余票查询成功! 正在发送车次信息...')
        # 发送格式化的车次信息
        # •  车次: D2222
        #     出发站: 武汉|六安
        #     到达站: 德清|南京南
        #     出发时间: 08:13
        #     到达时间: 12:21
        #     余票: 12|1|2|无
        #     ———————————-
        train_message = ''
        # 按照发车点排序
        collect_result = sorted(
            collect_result, key=lambda x: x.start_time, reverse=False)
        # 查询票价信息
        prices = query_train_price(
            train_date, stations[from_station], stations[to_station])
        prices_dict = get_price_dict(prices)
        for train in collect_result:
            # 如果是买长补短 则价格需要重新查询
            if train.train_code in long_buy_trains.keys() and len(long_buy_trains[train.train_code]) > 0 and train.to_station in long_buy_trains[train.train_code]:
                # 重新查询价格
                new_prices = query_train_price(train_date, train.from_station,
                                               train.to_station)
                new_prices_dict = get_price_dict(new_prices)
                try:
                    train_message = train_message + assemble_bot_msg(to_station, train, stations,
                                                                     reversed_stations, new_prices_dict, True)
                except:
                    traceback.print_exc()
                    continue
            else:
                try:
                    train_message = train_message + assemble_bot_msg(to_station, train, stations,
                                                                     reversed_stations, prices_dict, False)
                except:
                    traceback.print_exc()
                    continue
        # train_message = train_message + \
        #     f'[注]:\n1.余票格式【无座|二等座|一等座|特等座】【无座|硬座|硬卧|软卧】\n2.出发站/到站格式【起点|上车点】【终点|下车点】'
        console.log('余票查询成功!')
        bot.send_message(message.chat.id, train_message)

    except Exception as e:
        traceback.print_exc()
        bot.send_message(message.chat.id, f'请求过于频繁,请稍后尝试!\n\n{e}')
        return None

# ===========================test=========================================


# query_train_info('5l000D237302', 'UAH', 'HKN', '2023-10-19')

# handle(None, load_stations(), [Train(**{
#     'train_code': '5l0000G63700',
#     'train_no': 'G637',
#     'from_station': 'UAH',
#     'to_station': 'WHN',
#     'date': '2023-10-18',
#     'start_time': '08:48',
#     'arrive_time': '10:18',
#     'duration': '01:30',
#     'no_seat': '16',
#     'second_seat': '4',
#     'first_seat': '6',
#     'special_seat': '0'
# })])

# prices = query_train_price('2023-10-18', 'UAH', 'WHN')
pass
