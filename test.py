import datetime


with open('version', 'r+') as f:
    version = f.read()
    print('version: ', version)
last_date = version.rsplit('-', 1)[0]
# 如果和今天相差一个月 跳过
if (datetime.datetime.now() - datetime.datetime.strptime(last_date, '%Y-%m-%d')).days < 30:
    print('跳过')
    exit(0)
