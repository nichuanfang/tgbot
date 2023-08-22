# tmdb机器人
from tmdbv3api import TMDb
from tmdbv3api import Movie
from tmdbv3api import TV
from tmdbv3api import Trending
import telebot
import requests
from settings.config import tmdb_config
from datetime import datetime
from datetime import date
from bs4 import BeautifulSoup
import lxml

tmdb = TMDb()
tmdb.api_key = tmdb_config['TMDB_API_KEY']
# 'en' or 'zh'
tmdb.language = 'zh'
tmdb.debug = False

movie = Movie()
tv = TV()

TMDB_WEBHOOK_URL_PATH = "/%s/" % (tmdb_config['BOT_TOKEN'])

logger = telebot.logger

bot = telebot.TeleBot(tmdb_config['BOT_TOKEN'],threaded=False)

@bot.message_handler(commands=['movie'])
def movie_query(message):
    """电影查询

    Returns:
        _type_: _description_
    """    
    search_text = message.text[6:].strip()
    search = movie.search(search_text)
    for res in search:
        print(res.id)
        print(res.title)
        print(res.release_date)
        print(res.overview)
        print(res.poster_path)
        print(res.vote_average)
    bot.reply_to(message, '电影查询')

@bot.message_handler(commands=['tvshow'])
def tvshow_query(message):
    """剧集查询

    Args:
        message (_type_): _description_
    """   
    bot.reply_to(message, '剧集查询')


def webhook(app,flask,FLASK_URL_BASE):
    """设置webhook
    """    
    # Set webhook
    @app.route('/tmdb')
    def home():
        # 设置webhook
        bot.remove_webhook()
        # Set webhook
        bot.set_webhook(url=FLASK_URL_BASE + TMDB_WEBHOOK_URL_PATH,max_connections=1)
        return 'dogyun-Webhook设置成功!'

        
    # Process webhook calls
    @app.route(TMDB_WEBHOOK_URL_PATH, methods=['POST'],strict_slashes=False)
    def webhook():
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            flask.abort(403)

