#!/bin/bash
cp ../Boblebot-bf62eff2e7f4.json .
screen -S Bot_discord
python3 boblebot.py $DISCORD_TOKEN_ELDEN $APIKEY
