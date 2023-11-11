#!/bin/bash
docker stop tgbot
pip3.11 install -r requirements.txt
nohup python3.11 /root/code/tgbot/main.py >>/var/log/tgbot.log 2>&1 &
