#!/usr/bin/env python3
import discord
import os.path
import sys
import time
import datetime
import asyncio
import requests
import json

with open(sys.path[0] + '/keys.json', 'r') as f:
    key = json.load(f)
client = discord.Client()
print('Started...')

@client.event
async def on_ready():
    print('Sucessfully logged in as ' + client.user.id)

@client.event
async def on_message(message):
    if message.content.startswith('.price'):
        try:
            itemq = str(message.content.split(' ', 1)[1])
        except IndexError:
            return
        await client.send_typing(message.channel)
        if itemq == 'update':
            r = requests.get('http://backpack.tf/api/IGetPrices/v4?key=' + key['backpacktf'])
            if r.json()['response']['success'] != 1:
                await client.send_message(message.channel, str(r.json()['response']['message'].rsplit('.', 2)[0]) + '.')
            else:
                with open (sys.path[0] + '/bplist.json', 'w') as f:
                    json.dump(r.json(), f, indent=4)
                    await client.send_message(message.channel, 'Item price list updated')
        else:
            with open(sys.path[0] + '/bplist.json', 'r') as f:
                bpjs = json.load(f)
            try:
                itemobj = bpjs['response']['items'][itemq]['prices']['6']['Tradable']
                ipr = str(itemobj['Craftable'][0]['value'])
                cur = str(itemobj['Craftable'][0]['currency'])
            except KeyError:
                try:
                    ipr = str(itemobj['Non-Craftable'][0]['value'])
                    cur = str(itemobj['Non-Craftable'][0]['currency'])
                except (KeyError, UnboundLocalError):
                    await client.send_message(message.channel, 'Item not found')
                    return
            await client.send_message(message.channel, itemq + ' is currently priced at ' + ipr + ' ' + cur + '.')
    else:
        pass

client.run(key['discord'])