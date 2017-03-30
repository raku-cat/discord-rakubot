#!/usr/bin/env python3
import discord
import os.path
import sys
import asyncio
import aiohttp
import json
import string

with open(sys.path[0] + '/keys.json', 'r') as f:
    key = json.load(f)
client = discord.Client()
print('Started...')

@client.event
async def on_ready():
    print('Sucessfully logged in as ' + client.user.name + '(' + client.user.id + ')')

@client.event
async def on_message(message):
    if message.content.startswith('.price'):
        try:
            itemq = string.capwords(str(message.content.split(' ', 1)[1]))
        except IndexError:
            return
        await client.send_typing(message.channel)
        quality = ['Vintage', 'Genuine', 'Strange', 'Unusual', 'Haunted', 'Collector\'s']
        if any(qual in itemq for qual in quality):
            qual = str([item for item in quality if item in itemq][0])
            params = "&quality=" + qual + "&item=" + str(itemq.split(' ')[1])
        else:
            params = "&item=" + itemq + "&quality=6"
        async with aiohttp.get('http://backpack.tf/api/IGetPriceHistory/v1?key=' + key['backpacktf'] + params) as r:
            if r.status == 200:
                js = await r.json()
                try:
                    if js['response']['success'] == 1:
                        itemob = js['response']['history'][-1]
                        ipr = str(itemob['value'])
                        cur = str(itemob['currency'])
                        await client.send_message(message.channel, itemq + ' is currently priced at ' + ipr + ' ' + cur + '.')
                    else:
                        await client.send_message(message.channel, "Something went wrong")
                except json.decoder.JSONDecodeError:
                    await client.send_message(message.channel, 'Item not found')
    else:
        pass

client.run(key['discord'])