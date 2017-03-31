#!/usr/bin/env python3
import discord
from titlecase import titlecase
import sys
import asyncio, aiofiles
import json
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
    inmsg = message.content.lower()
    if inmsg.startswith('.price'):
        try:
            itemq = titlecase(str(message.content.split(' ', 1)[1]))
        except IndexError:
            return
        client.send_typing(message.channel)
        if any(x in ' '+inmsg+' ' for x in [' .price ', ' .price@bptf ']):
            pricemsg = await parse_bptf_query(itemq)
        elif inmsg.startswith('.price@scm'):
            pricemsg = await parse_scm_query(itemq)
        else:
            return
        await client.send_message(message.channel, pricemsg)
    else:
        return
async def parse_scm_query(itemq):
    prams = { 'currency' : 1, 'appid' : 440, 'market_hash_name': itemq }
    r = requests.get('https://steamcommunity.com/market/priceoverview/', params=prams)
    if r.status_code == 200 or 500:
        js = r.json()
        if str(js['success']) == 'True':
            try:
                ipr = str(js['lowest_price'])
                return '**' + itemq + '** is currently priced at *' + ipr + '*.'
            except KeyError:
                return 'No price found.'
        else:
            return 'Item not found.'
    else:
        return 'Something went wrong.'

async def parse_bptf_query(itemq):
    quality = ['Vintage', 'Genuine', 'Strange', 'Haunted', 'Collector\'s']
    async with aiofiles.open(sys.path[0] + '/unuschem.json', mode='r') as unusch:
        unu = json.loads(await unusch.read())
        unuef = [ row['name'] for row in unu ]
    prams = { 'key' : key['backpacktf'], 'item' : itemq, 'quality' : 6 }
    if any(qual in itemq for qual in quality):
        qual = str([item for item in quality if item in itemq][0])
        prams.update({ 'item' :  prams['item'].replace(qual, '').lstrip(), 'quality' : qual})
    if any(effect in itemq for effect in unuef):
        effectn = str([item for item in unuef if item in itemq][0])
        effectid = str([item for item in unu if item['name'] == effectn][0]['id'])
        prams.update({ 'item' : prams['item'].replace(effectn, '').lstrip(), 'quality' : 5, 'priceindex' : effectid })
    else:
        pass
    r = requests.get('https://backpack.tf/api/IGetPriceHistory/v1', params=prams)
    #print(r.url)
    if r.status_code == 200:
        try:
            js = r.json()
            if js['response']['success'] == 1:
                try:
                    itemob = js['response']['history'][-1]
                except IndexError:
                    return 'No price found'
                ipr = str(itemob['value'])
                cur = str(itemob['currency'])
                return '**' + itemq + '** is currently priced at *' + ipr + ' ' + cur + '*.'
            else:
                return 'Something went wrong.'
        except json.decoder.JSONDecodeError:
            return 'Item not found.'

client.run(key['discord'])
