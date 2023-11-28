import time
import flask
import telebot

# webhook监听地址
WEBHOOK_LISTEN = '0.0.0.0'
# 证书路径
WEBHOOK_SSL_CERT = '/cert/cert.pem'
# 根路径
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, 443)


def set_webhook_host(host: str):
    """设置webhook_host

    Args:
        host (str): _description_
    """
    global WEBHOOK_HOST
    WEBHOOK_HOST = host


def register_webhook(bot: telebot.TeleBot, hook_data: list):
    """注册webhook

    Args:
        bot (telebot.TeleBot): _description_
    """
    WEBHOOK_URL_PATH = f"/{bot.token}/"
    # Remove webhook, it fails sometimes the set if there is a previous webhook
    bot.remove_webhook()
    time.sleep(0.1)

    # Set webhook
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))
    hook_data.append({
        'bot': bot,
        'webhook_url': WEBHOOK_URL_PATH
    })


def run(hook_data: list[dict]):
    """运行flask
    """
    app = flask.Flask(__name__)

    for hook in hook_data:
        bot = hook['bot']
        webhook_url = hook['webhook_url']

        @app.route(webhook_url, methods=['POST'])
        def webhook():
            if flask.request.headers.get('content-type') == 'application/json':
                json_string = flask.request.get_data().decode('utf-8')
                update = telebot.types.Update.de_json(json_string)
                bot.process_new_updates([update])
                return ''
            else:
                flask.abort(403)

    # Start flask server
    app.run(host=WEBHOOK_LISTEN,
            port=8888,
            debug=True)
