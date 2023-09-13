import telebot
from  telebot.types import Message
import requests
from settings.config import tmdb_config
import json
from tmdbv3api import TMDb
from tmdbv3api import Movie
from tmdbv3api import TV

tmdb = TMDb()

tmdb.api_key = tmdb_config['API_KEY']
tmdb.language = 'zh-CN'

movie = Movie()

tv = TV()

logger = telebot.logger

bot = telebot.TeleBot(tmdb_config['BOT_TOKEN'],threaded=False)

@bot.message_handler(commands=['movie_popular'])
def movie_popular(message):
    res = movie.popular()
    movie_text = '*电影推荐:*\n'
    for movie_res in res.results:
        movie_name = f'{movie_res.title} ({movie_res["release_date"].split("-")[0]})'
        movie_tmdb_url = f'https://www.themoviedb.org/movie/{movie_res.id}?language=zh-CN'
        movie_text = movie_text + f'·  `{movie_name}`      [🔗]({movie_tmdb_url})\n'
    bot.send_message(message.chat.id,movie_text,'MarkdownV2')


@bot.message_handler(commands=['tv_popular'])
def tv_popular(message):
    res = tv.popular()
    tv_text = '*剧集推荐:*\n'
    for tv_res in res.results:
        tv_name = f'{tv_res.name} ({tv_res["first_air_date"].split("-")[0]})'
        tv_tmdb_url = f'https://www.themoviedb.org/tv/{tv_res.id}?language=zh-CN'
        tv_text = tv_text + f'·  `{tv_name}`      [🔗]({tv_tmdb_url})\n'
    
    bot.send_message(message.chat.id,tv_text,'MarkdownV2')

@bot.message_handler(commands=['movie_search'])
def search_movie(message):
    """获取TMDB电影信息

    Returns:
        _type_: _description_
    """ 
    movie_text = '*电影结果:*\n'
    movie_search  = movie.search(message.text[14:])
    for movie_res in movie_search.results:
        movie_name = f'{movie_res.title} ({movie_res["release_date"].split("-")[0]})'
        movie_tmdb_url = f'https://www.themoviedb.org/movie/{movie_res.id}?language=zh-CN'
        movie_text = movie_text + f'·  `{movie_name}`      [🔗]({movie_tmdb_url})\n'
    if len(movie_search.results) != 0:
        bot.send_message(message.chat.id,movie_text,'MarkdownV2')
    
@bot.message_handler(commands=['tv_search'])
def search_tv(message):
    """获取TMDB剧集信息

    Returns:
        _type_: _description_
    """ 
    tv_text = '*剧集结果:*\n'
    tv_search = tv.search(message.text[11:])
    for tv_res in tv_search.results:
        tv_name = f'{tv_res.name} {tv_res.original_name} ({tv_res["first_air_date"].split("-")[0]})'
        tv_tmdb_url = f'https://www.themoviedb.org/tv/{tv_res.id}?language=zh-CN'
        tv_text = tv_text + f'·  `{tv_name}`      [🔗]({tv_tmdb_url})\n'
    if len(tv_search.results) != 0:
        bot.send_message(message.chat.id,tv_text,'MarkdownV2')
    
    
@bot.message_handler(content_types=['text'])
def common(message):
    raw_msg = message.text.strip().replace(' ', '')
    if raw_msg and not raw_msg.startswith('/'):
        message.text = '/movie_search '+raw_msg
        search_movie(message)
        message.text = '/tv_search '+raw_msg
        search_tv(message)