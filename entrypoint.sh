#!/bin/bash

# 获取环境变量

exec python config_gen $TGBOT_TOKEN &
exec python main.py
