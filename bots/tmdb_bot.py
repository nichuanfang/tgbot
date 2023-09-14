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
        try:
            if movie_res["release_date"] == None or movie_res["release_date"] == '':
                release_date = ''
            else:
                release_date = '('+movie_res["release_date"].split("-")[0]+')'
        except:
            release_date = ''
        if movie_res.original_title == movie_res.title:
            movie_name = f'{movie_res.title} {release_date}'
        else:
            movie_name = f'{movie_res.title} {movie_res.original_title} {release_date}'
        movie_tmdb_url = f'https://www.themoviedb.org/movie/{movie_res.id}?language=zh-CN'
        movie_text = movie_text + f'·  `{movie_name}`      [🔗]({movie_tmdb_url})\n'
    bot.send_message(message.chat.id,movie_text,'MarkdownV2')


@bot.message_handler(commands=['tv_popular'])
def tv_popular(message):
    res = tv.popular()
    tv_text = '*剧集推荐:*\n'
    for tv_res in res.results:
        try:
            if tv_res["first_air_date"] == None or tv_res["first_air_date"] == '':
                first_air_date = ''
            else:
                first_air_date = '('+tv_res["first_air_date"].split("-")[0]+')'
        except:
            first_air_date = ''
        if tv_res.original_name == tv_res.name:
            tv_name = f'{tv_res.name} {first_air_date}'
        else:
            tv_name = f'{tv_res.name} {tv_res.original_name} {first_air_date}'
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
        try:
            if movie_res["release_date"] == None or movie_res["release_date"] == '':
                release_date = ''
            else:
                release_date = '('+movie_res["release_date"].split("-")[0]+')'
        except:
            release_date = ''
        if movie_res.original_title == movie_res.title:
            movie_name = f'{movie_res.title} {release_date}'
        else:
            movie_name = f'{movie_res.title} {movie_res.original_title} {release_date}'
        movie_tmdb_url = f'https://www.themoviedb.org/movie/{movie_res.id}?language=zh-CN'
        movie_text = movie_text + f'·  `{movie_name}`      [🔗]({movie_tmdb_url})\n'
    if len(movie_search.results) != 0:
        bot.send_message(message.chat.id,movie_text,'MarkdownV2')
    else:
        return None
    
@bot.message_handler(commands=['tv_search'])
def search_tv(message):
    """获取TMDB剧集信息

    Returns:
        _type_: _description_
    """ 
    tv_text = '*剧集结果:*\n'
    tv_search = tv.search(message.text[11:])
    for tv_res in tv_search.results:
        try:
            if tv_res["first_air_date"] == None or tv_res["first_air_date"] == '':
                first_air_date = ''
            else:
                first_air_date = '('+tv_res["first_air_date"].split("-")[0]+')'
        except:
            first_air_date = ''
        if tv_res.original_name == tv_res.name:
            tv_name = f'{tv_res.name} {first_air_date}'
        else:
            tv_name = f'{tv_res.name} {tv_res.original_name} {first_air_date}'
        tv_tmdb_url = f'https://www.themoviedb.org/tv/{tv_res.id}?language=zh-CN'
        tv_text = tv_text + f'·  `{tv_name}`      [🔗]({tv_tmdb_url})\n'
    if len(tv_search.results) != 0:
        bot.send_message(message.chat.id,tv_text,'MarkdownV2')
    else:
        return None
    
    
@bot.message_handler(content_types=['text'])
def common(message):
    raw_msg = message.text.strip().replace(' ', '')
    if raw_msg and not raw_msg.startswith('/'):
        message.text = '/movie_search '+raw_msg
        movie_res = search_movie(message)
        message.text = '/tv_search '+raw_msg
        tv_res = search_tv(message)
        if movie_res == None and tv_res == None:
            bot.reply_to(message,'未找到任何电影剧集!')