import telebot
from bots import dogyun_bot
from bots.dogyun_bot import scheduler
from settings import config
from settings.config import dogyun_config
from settings.config import flask_config
import logging

# 设置tg的日志
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

FLASK_URL_BASE = flask_config['FLASK_URL_BASE']

class Config(object):
    SCHEDULER_API_ENABLED = True

if __name__ == '__main__':
    
    # run
    if config.ENV == "DEV":
        # 本地测试单个机器人
        dogyun_bot.bot.remove_webhook()
        dogyun_bot.bot.infinity_polling() 


    elif config.ENV == "PROD":
        import flask
        from flask import Flask, request
        
        
        app = flask.Flask(__name__)
        
        app.config.from_object(Config())
        
        scheduler.init_app(app)
        scheduler.start()
        
        # 禁止爬虫
        @app.route('/robots.txt')
        def robots():
            return "User-agent: *\nDisallow: /", 200
        
        # 设置webhook
        dogyun_bot.webhook(app,flask,FLASK_URL_BASE)
        
        
        # Start flask server
        app.run(host=flask_config['FLASK_LISTEN'],
                port=flask_config['FLASK_PORT'],
                ssl_context=(flask_config['FLASK_SSL_CERT'], flask_config['FLASK_SSL_PRIV']),
                debug=False)