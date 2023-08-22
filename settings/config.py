# 环境'DEV' or 'PROD'
ENV = 'PROD'

flask = {
    'FLASK_HOST': 'bot.cinima.asia',
    'FLASK_PORT': 88,  # 443, 80, 88 or 8443 (port need to be 'open')
    'FLASK_LISTEN': '0.0.0.0.',
    'FLASK_SSL_CERT': '/root/code/docker/dockerfile_work/xray/cert/cert.pem',
    'FLASK_SSL_PRIV': '/root/code/docker/dockerfile_work/xray/cert/key.pem',
    'FLASK_URL_BASE': 'https://%s:%s' % ('bot.cinima.asia', 88),
}

dogyun = {
    # 'DEV' or 'PROD'
    'ENV': 'DEV',
    # tg配置   
    'BOT_TOKEN': '6520766917:AAF6FUTwzpPYa0f0jq3LAVT8nRze4xH0F7w',
    'CHAT_ID': 5913565300,  
    # dogyun相关
    'DOGYUN_API_KEY': 'CX75AKIJOGQY3JUGG5DJF3RMQX0KV0ORT5PL',
    'DOGYUN_SERVER_ID': '40179',
    'DOGYUN_CSRF_TOKEN': '566cfb52-a04a-4a73-aed6-835b035c7087',
    'DOGYUN_COOKIE': 'SESSION=OTY3ZmRjMzQtMmFiMi00ZjdiLWI2YjQtZWM5MTBiOTkxYTM2'
}