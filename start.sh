#!/bin/bash
nohup python3.8 bot.py >>/var/log/tgbot.log 2>&1 &
