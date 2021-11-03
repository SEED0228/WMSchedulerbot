import discord
import requests
import json
from dotenv import load_dotenv
from os import getenv

# オブジェクトを取得
client = discord.Client()

# 文字列を空白区切りでリスト化
async def split_command(content):
    args = content.replace('　', ' ').split(' ')
    while '' in args:
        args.remove('')
    return args

async def check_validation(params, errors):
    return errors

async def create_link(params):
    link = 'https://waseda-moodle-scheduler.herokuapp.com/api/v1/events?'
    for key in params:
        link += f"{key}={params[key]}&"
    return link[:-1]

async def show_event_information(ctx, link, params):
    r = requests.get(link, headers={'Authorization': f"Basic {getenv('BASIC_AUTHORIZATION')}"})
    str = ''
    for key in params:
        str += f"{key}: {params[key]},"
    if r.status_code == 200:
        data = json.loads(r.text)
        embed = discord.Embed(title='検索結果', description=str[:-1], color=0x00ff00)
        for event in data:
            embed.add_field(name=f"{event['title']}", value=f"{event['uid'][:-20]}, {event['subject']}, {event['begin_at']}", inline=False)
    else:
        embed = discord.Embed(title='ERROR', description='Something is wrong', color=0xff0000)
    await ctx.channel.send(embed=embed)

async def show(ctx, args):
    parmit_commands = {'title': 'title', 'subject': 'subject', 'from': 'from_deadline', 'to': 'to_deadline', 'order': 'order', 'limit': 'limit'}
    params = {}
    errors = []
    if len(args) <= 2:
        errors.append({'name': "引数エラー", 'value': '引数が少なすぎます'})
    for arg in args[2:]:
        attrs = arg.split('=')
        if len(attrs) == 1:
            params['subject'] = attrs[0]
        elif len(attrs) == 2:
            if attrs[0] in parmit_commands:
                params[parmit_commands[attrs[0]]] = attrs[1]
            else:
                errors.append({'name': "引数エラー", 'value': '属性名が不正です'})
        else:
            errors.append({'name': "引数エラー", 'value': '=が多すぎます'})
    errors = await check_validation(params, errors)
    if errors:
        embed = discord.Embed(title='hoge', description='fuga', color=0xff0000)
        embed.title = "ERROR"
        embed.description = "Something is wrong"
        embed.color = 0xff0000
        for err in errors:
            embed.add_field(name=err['name'], value=err['value'], inline=False)
        await ctx.channel.send(embed=embed)
    else:
        await show_event_information(ctx, await create_link(params), params)

            
# コマンド処理
async def exec_command(ctx, args):
    if args[1] == 'show':
        await show(ctx, args)

@client.event
async def on_ready():
    # サーバー起動時に実行
    print('サーバーを起動します。')

@client.event
async def on_message(ctx):
    # Botのメッセージは除外
    if ctx.author.bot:
        return
    # 文字列を空白区切りでリスト化
    args = await split_command(ctx.content)
    # /wsmであれば実行
    if args[0] == '/wms':
        await exec_command(ctx, args)

# 実行
client.run(getenv('DISCORD_BOT_TOKEN'))
