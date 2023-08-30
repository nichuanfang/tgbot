import telebot
import requests
from settings.config import tmdb_config
import json
from tmdbv3api import TMDb
from tmdbv3api import Movie
from tmdbv3api import TV

tmdb = TMDb()

tmdb.api_key = tmdb_config['API_KEY']

movie = Movie()

tv = TV()

logger = telebot.logger

bot = telebot.TeleBot(tmdb_config['BOT_TOKEN'],threaded=False)

@bot.message_handler(commands=['movie_popular'])
def movie_popular(message):
    res = movie.popular()
    bot.reply_to(message,res._json['results'])


@bot.message_handler(commands=['tv_popular'])
def tv_popular(message):
    res = tv.popular()
    bot.reply_to(message,res._json['results'])


@bot.message_handler()
def search(message):
    """获取TMDB信息

    Returns:
        _type_: _description_
    """ 
    search  = movie.search(message.text)
    for res in search:
        print(res.id)
        print(res.title)
        print(res.overview)
        print(res.poster_path)
        print(res.vote_average)
        
    show = tv.search(message.text)
    for result in show:
        print(result.name)
        print(result.overview)