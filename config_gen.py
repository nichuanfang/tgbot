# 根据密钥构建配置文件settings/config.py
import os
import sys
import base64

# 获取第一个参数
if len(sys.argv) < 2:
    print("Github Actions Secret: TGBOT_TOKEN is required")
    sys.exit(1)
TGBOT_TOKEN = sys.argv[1]

# 构建配置文件
# base64解码
token = base64.decodebytes(TGBOT_TOKEN.encode()).decode()

# 写入config.py中
with open('settings/config.py', 'w+', encoding='utf-8') as f:
    f.write(token)
