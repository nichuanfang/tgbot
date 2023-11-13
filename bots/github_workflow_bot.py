import telebot
import requests
from settings.config import github_config
import json

logger = telebot.logger

bot = telebot.TeleBot(github_config['BOT_TOKEN'], threaded=False)


@bot.message_handler(commands=['scrape_metadata'])
def scrape_metadata(message):
    """刮削影视元信息

    Returns:
        _type_: _description_
    """
    header = {
        'Accept': 'application/vnd.github.everest-preview+json',
        'Authorization': f'token {github_config["GITHUB_TOKEN"]}'
    }
    requests.post('https://api.github.com/repos/nichuanfang/movie-tvshow-spider/dispatches',
                  data=json.dumps({"event_type": "crawl movies and shows"}), headers=header)
    bot.reply_to(
        message, '已触发工作流: 刮削影视元信息,查看刮削日志: https://github.com/nichuanfang/movie-tvshow-spider/actions')


@bot.message_handler(commands=['update_proxy'])
def update_proxy(message):
    """更新备用代理池

    Returns:
        _type_: _description_
    """
    header = {
        'Accept': 'application/vnd.github.everest-preview+json',
        'Authorization': f'token {github_config["GITHUB_TOKEN"]}'
    }
    requests.post('https://api.github.com/repos/nichuanfang/nogfw/dispatches',
                  data=json.dumps({"event_type": "更新备用代理池"}), headers=header)
    bot.reply_to(message, '已触发工作流: 更新备用代理池')


@bot.message_handler(commands=['generate_girlfriend_chat'])
def generate_girlfriend_chat(message):
    """生成每日女友问候

    Returns:
        _type_: _description_
    """
    header = {
        'Accept': 'application/vnd.github.everest-preview+json',
        'Authorization': f'token {github_config["GITHUB_TOKEN"]}'
    }
    requests.post('https://api.github.com/repos/nichuanfang/wechat-girlfriend-push/dispatches',
                  data=json.dumps({"event_type": "生成每日女友问候"}), headers=header)
    bot.reply_to(message, '已触发工作流: 生成每日女友问候')


@bot.message_handler(commands=['update_everyday_wallpaper'])
def update_everyday_wallpaper(message):
    """ 更新每日壁纸

    Returns:
        _type_: _description_
    """
    header = {
        'Accept': 'application/vnd.github.everest-preview+json',
        'Authorization': f'token {github_config["GITHUB_TOKEN"]}'
    }
    requests.post('https://api.github.com/repos/nichuanfang/nichuanfang/dispatches',
                  data=json.dumps({"event_type": " 更新每日壁纸"}), headers=header)
    bot.reply_to(message, '已触发工作流: 更新每日壁纸')
