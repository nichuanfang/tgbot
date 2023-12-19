# import telebot
from bots import dogyun_bot
from bots.dogyun_bot import lucky_draw_notice, balance_lack_notice
from bots import github_workflow_bot
from bots import tmdb_bot
from bots import train_bot
from util.my_logging import logger
import threading
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()


def dogyun_bot_func():
    dogyun_bot.bot.remove_webhook()
    # 启动轮询
    dogyun_bot.bot.infinity_polling(long_polling_timeout=60)


def github_workflow_bot_func():
    github_workflow_bot.bot.remove_webhook()
    github_workflow_bot.bot.infinity_polling(long_polling_timeout=60)


def tmdb_bot_func():
    tmdb_bot.bot.remove_webhook()
    tmdb_bot.bot.infinity_polling(long_polling_timeout=60)


def train_bot_func():
    train_bot.bot.remove_webhook()
    train_bot.bot.infinity_polling(long_polling_timeout=60)


def scheduler_func():
    # 每月7号获取流量包
    # scheduler.add_job(get_traffic_packet, 'cron', id='get_traffic_packet',
    #                   month='*', day='7', hour='9', minute='0', second='0')
    # 每天9点通知抽奖活动
    scheduler.add_job(lucky_draw_notice, 'cron', id='lucky_draw_notice',
                      month='*', day='*', hour='9', minute='0', second='0')
    # 每天9点通知余额不足
    scheduler.add_job(balance_lack_notice, 'cron', id='balance_lack_notice',
                      month='*', day='*', hour='9', minute='0', second='0')
    logger.info('Scheduler started!')
    # 开启定时任务
    scheduler.start()


if __name__ == '__main__':
    thread1 = threading.Thread(target=dogyun_bot_func, daemon=True)
    thread2 = threading.Thread(target=github_workflow_bot_func, daemon=True)
    thread3 = threading.Thread(target=tmdb_bot_func, daemon=True)
    thread4 = threading.Thread(target=train_bot_func, daemon=True)
    thread5 = threading.Thread(target=scheduler_func, daemon=True)

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()

    thread1.join()
