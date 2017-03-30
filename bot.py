#!/usr/bin/env python3
import discord
import os.path
import sys
import asyncio
import aiohttp
import aiofiles
import json
import string
import requests

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
        await client.send_message(message.channel, await parse_query(itemq))
    else:
        return

async def parse_query(itemq):
    quality = ['Vintage', 'Genuine', 'Strange', 'Unusual', 'Haunted', 'Collector\'s']
    async with aiofiles.open(sys.path[0] + '/unuschem.json', mode='r') as unusch:
        unu = json.loads(await unusch.read())
        unuef = [ row['name'] for row in unu ]
    if any(qual in itemq for qual in quality):
        qual = str([item for item in quality if item in itemq][0])
        params = "&quality=" + qual + "&item=" + str(itemq.split(' ')[1])
    elif any(effect in itemq for effect in unuef):
        effectn = str([item for item in unuef if item in itemq][0])
        effectid = str([item for item in unu if item['name'] == effectn][0]['id'])
        params = "&item=" + itemq.replace(effectn, '').lstrip() + "&quality=5" + "&priceindex=" + effectid
    else:
        params = "&item=" + itemq + "&quality=6"
    r = requests.get('http://backpack.tf/api/IGetPriceHistory/v1?key=' + key['backpacktf'] + params)
    if r.status_code == 200:
        try:
            js = r.json()
            if js['response']['success'] == 1:
                itemob = js['response']['history'][-1]
                ipr = str(itemob['value'])
                cur = str(itemob['currency'])
                return itemq + ' is currently priced at ' + ipr + ' ' + cur + '.'
            else:
                return 'Something went wrong.'
        except json.decoder.JSONDecodeError:
            return 'Item not found.'

client.run(key['discord'])
