#!/usr/bin/env python3
import discord
import os.path
from titlecase import titlecase
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
    if message.content.lower().startswith('.price'):
        try:
            itemq = titlecase(str(message.content.split(' ', 1)[1]))
        except IndexError:
            return
        await client.send_typing(message.channel)
        await client.send_message(message.channel, await parse_query(itemq))
    else:
        return

async def parse_query(itemq):
    quality = ['Vintage', 'Genuine', 'Strange', 'Haunted', 'Collector\'s']
    async with aiofiles.open(sys.path[0] + '/unuschem.json', mode='r') as unusch:
        unu = json.loads(await unusch.read())
        unuef = [ row['name'] for row in unu ]
    prams = { 'key' : key['backpacktf'], 'item' : itemq, 'quality' : 6 }
    if any(qual in itemq for qual in quality):
        qual = str([item for item in quality if item in itemq][0])
        prams['quality'] = qual
        prams['item'] = prams['item'].replace(qual, '').lstrip()
    if any(effect in itemq for effect in unuef):
        effectn = str([item for item in unuef if item in itemq][0])
        effectid = str([item for item in unu if item['name'] == effectn][0]['id'])
        prams['priceindex'] = effectid
        prams['item'] = prams['item'].replace(effectn, '').lstrip()
        prams['quality'] = 5
    else:
        pass
    r = requests.get('http://backpack.tf/api/IGetPriceHistory/v1', params=prams)
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
