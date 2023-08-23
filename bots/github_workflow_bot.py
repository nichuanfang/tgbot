import telebot
import requests
from settings.config import dogyun_config
from settings.config import github_config
import json

GITHUB_WEBHOOK_URL_PATH = "/%s/" % (github_config['BOT_TOKEN'])

logger = telebot.logger

bot = telebot.TeleBot(github_config['BOT_TOKEN'],threaded=False)

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
    requests.post('https://api.github.com/repos/nichuanfang/movie-tvshow-spider/dispatches',data=json.dumps({"event_type": "刮削影视元信息"}),headers=header)
    bot.reply_to(message, '已触发工作流: 刮削影视元信息')
    
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
    requests.post('https://api.github.com/repos/nichuanfang/nogfw/dispatches',data=json.dumps({"event_type": "更新备用代理池"}),headers=header)
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
    requests.post('https://api.github.com/repos/nichuanfang/wechat-girlfriend-push/dispatches',data=json.dumps({"event_type": "生成每日女友问候"}),headers=header)
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
    requests.post('https://api.github.com/repos/nichuanfang/nichuanfang/dispatches',data=json.dumps({"event_type": " 更新每日壁纸"}),headers=header)
    bot.reply_to(message, '已触发工作流: 更新每日壁纸')

def webhook(app,flask,FLASK_URL_BASE):
    """设置webhook
    """    
    # Set webhook
    @app.route('/github')
    def github():
        # 设置webhook
        bot.remove_webhook()
        # Set webhook
        bot.set_webhook(url=FLASK_URL_BASE + GITHUB_WEBHOOK_URL_PATH,max_connections=1)
        return 'github-Webhook设置成功!'

        
    # Process webhook calls
    @app.route(GITHUB_WEBHOOK_URL_PATH, methods=['POST'],strict_slashes=False)
    def github_webhook():
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            flask.abort(403)

