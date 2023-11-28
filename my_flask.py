import time
import flask
import telebot

from my_telebot import TeleBot

# flask监听地址
WEBHOOK_LISTEN = '0.0.0.0'
# flask监听端口 默认8888
WEBHOOK_LISTEN_PORT = 8888
# 证书路径
WEBHOOK_SSL_CERT = '/cert/cert.pem'


def register_webhook(bot: telebot.TeleBot, WEBHOOK_HOST: str, hook_data: list):
    """注册webhook

    Args:
        bot (telebot.TeleBot): _description_
    """
    WEBHOOK_URL_BASE = f'https://{WEBHOOK_HOST}'
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
        bot: TeleBot = hook['bot']
        bot_name = bot.get_my_name()
        webhook_url = hook['webhook_url']

        if bot_name == 'DogyunBot':
            print(f'定义webhook:{bot_name}')

            @app.route(webhook_url, methods=['POST'])
            def dogyun_bot_webhook():
                if flask.request.headers.get('content-type') == 'application/json':
                    json_string = flask.request.get_data().decode('utf-8')
                    update = telebot.types.Update.de_json(json_string)
                    bot.process_new_updates([update])
                    return ''
                else:
                    flask.abort(403)
        elif bot_name == 'MyTmdbBot':
            print(f'定义webhook:{bot_name}')

            @app.route(webhook_url, methods=['POST'])
            def tmdb_webhook():
                if flask.request.headers.get('content-type') == 'application/json':
                    json_string = flask.request.get_data().decode('utf-8')
                    update = telebot.types.Update.de_json(json_string)
                    bot.process_new_updates([update])
                    return ''
                else:
                    flask.abort(403)
        elif bot_name == 'GithubWorkflowBot':
            print(f'定义webhook:{bot_name}')

            @app.route(webhook_url, methods=['POST'])
            def github_webhook():
                if flask.request.headers.get('content-type') == 'application/json':
                    json_string = flask.request.get_data().decode('utf-8')
                    update = telebot.types.Update.de_json(json_string)
                    bot.process_new_updates([update])
                    return ''
                else:
                    flask.abort(403)
        elif bot_name == 'TrainBot':
            print(f'定义webhook:{bot_name}')

            @app.route(webhook_url, methods=['POST'])
            def train_bot_webhook():
                if flask.request.headers.get('content-type') == 'application/json':
                    json_string = flask.request.get_data().decode('utf-8')
                    update = telebot.types.Update.de_json(json_string)
                    bot.process_new_updates([update])
                    return ''
                else:
                    flask.abort(403)

    # Start flask server
    app.run(host=WEBHOOK_LISTEN,
            port=WEBHOOK_LISTEN_PORT,
            debug=True)
