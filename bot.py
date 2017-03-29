#!/usr/bin/env python3
import discord
#import logging
import sys
import time
import datetime
import asyncio
import requests

#logger = logging.basicConfig(level=logging.DEBUG)
with open(sys.path[0] + '/token.txt', 'r') as f:
    token=f.read().strip('\n')
client = discord.Client()
print('Started...')
r = requests.get("http://backpack.tf/api/IGetPrices/v4?key=58dbd990c440456a5523ffdb")
@client.event
async def on_ready():
    print('Sucessfully logged in as ' + client.user.id)
#    print(value(discord.Permissions.send_messages))

@client.event
async def on_message(message):
#    print('Message received')
#    print(message.content)
#    print(message.channel.id)
    if message.content.startswith('.price'):
        #r = requests.get("http://backpack.tf/api/IGetPrices/v4?key=58dbd990c440456a5523ffdb")
        print(r.json()['response'],['message'])
        await client.send_message(message.channel, r.json())
    else:
        pass

client.run(token)