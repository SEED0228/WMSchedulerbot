import discord
import requests
import json
from dotenv import load_dotenv
from os import getenv
from datetime import datetime as dt

# オブジェクトを取得
client = discord.Client()

# 文字列を空白区切りでリスト化
def split_command(content):
    args = content.replace("　", " ").split(" ")
    while "" in args:
        args.remove("")
    return args


def check_validation(params, errors):
    return errors


def create_link(name, params):
    link = f"https://waseda-moodle-scheduler.herokuapp.com/api/v1/{name}?"
    for key in params:
        link += f"{key}={params[key]}&"
    return link[:-1]


async def show_event_information(ctx, params):
    link = create_link("events", params)
    r = requests.get(
        link, headers={"Authorization": f"Basic {getenv('BASIC_AUTHORIZATION')}"}
    )
    str = ""
    for key in params:
        str += f"{key}: {params[key]},"
    if r.status_code == 200:
        data = json.loads(r.text)
        embed = discord.Embed(title="検索結果", description=str[:-1], color=0x00FF00)
        for event in data:
            embed.add_field(
                name=f"{event['title']}",
                value=f"{event['uid'][:-20]}, {event['subject']}, {event['begin_at']}",
                inline=False,
            )
    else:
        embed = discord.Embed(
            title="ERROR", description="Something is wrong", color=0xFF0000
        )
    await ctx.channel.send(embed=embed)


async def show_progress_information(ctx, params):
    link = create_link("events/progresses", params)
    r = requests.get(
        link, headers={"Authorization": f"Basic {getenv('BASIC_AUTHORIZATION')}"}
    )
    status = {
        0: "todo",
        1: "doing",
        2: "done",
    }
    str = ""
    for key in params:
        str += (
            f"{key}: {params[key]},"
            if key != "status"
            else f"{key}: {status[int(params[key])]},"
        )
    if r.status_code == 200:
        data = json.loads(r.text)
        embed = discord.Embed(
            title=f"検索結果({params['username']})", description=str[:-1], color=0x00FF00
        )
        for progress in data:
            embed.add_field(
                name=f"{status[progress['status']]}:{progress['event']['title']}",
                value=f"{progress['event']['uid'][:-20]}, {progress['event']['subject']}, {progress['event']['begin_at']}",
                inline=False,
            )
    else:
        embed = discord.Embed(
            title="ERROR", description="Something is wrong", color=0xFF0000
        )
    await ctx.channel.send(embed=embed)


async def show(ctx, args):
    parmit_commands = {
        "title": "title",
        "subject": "subject",
        "from": "from_deadline",
        "to": "to_deadline",
        "order": "order",
        "limit": "limit",
    }
    params = {"from_deadline": dt.now().strftime("%Y%m%d")}
    errors = []
    if len(args) <= 2:
        errors.append({"name": "引数エラー", "value": "引数が少なすぎます"})
    for arg in args[2:]:
        attrs = arg.split("=")
        if len(attrs) == 1:
            params["subject"] = attrs[0]
        elif len(attrs) == 2:
            if attrs[0] in parmit_commands:
                params[parmit_commands[attrs[0]]] = attrs[1]
            else:
                errors.append({"name": "引数エラー", "value": "属性名が不正です"})
        else:
            errors.append({"name": "引数エラー", "value": "=が多すぎます"})
    errors = check_validation(params, errors)
    if errors:
        embed = discord.Embed(title="hoge", description="fuga", color=0xFF0000)
        embed.title = "ERROR"
        embed.description = "Something is wrong"
        embed.color = 0xFF0000
        for err in errors:
            embed.add_field(name=err["name"], value=err["value"], inline=False)
        await ctx.channel.send(embed=embed)
    else:
        await show_event_information(ctx, params)


async def check(ctx, args):
    parmit_commands = {
        "title": "title",
        "subject": "subject",
        "from": "from_deadline",
        "to": "to_deadline",
        "order": "order",
        "limit": "limit",
        "username": "username",
        "s": "status",
        "status": "status",
    }
    status = {
        "todo": "0",
        "doing": "1",
        "done": "2",
        "0": "0",
        "1": "1",
        "2": "2",
    }
    params = {"from_deadline": dt.now().strftime("%Y%m%d")}
    errors = []
    if len(args) <= 2:
        errors.append({"name": "引数エラー", "value": "引数が少なすぎます"})
    else:
        params["username"] = args[2]
    for arg in args[3:]:
        attrs = arg.split("=")
        if len(attrs) == 1:
            params["subject"] = attrs[0]
        elif len(attrs) == 2:
            if attrs[0] in parmit_commands:
                if attrs[0] in {"s", "status"}:
                    if attrs[1] in status:
                        attrs[1] = status[attrs[1]]
                    else:
                        errors.append({"name": "引数エラー", "value": "属性名が不正です"})
                params[parmit_commands[attrs[0]]] = attrs[1]
            else:
                errors.append({"name": "引数エラー", "value": "属性名が不正です"})
        else:
            errors.append({"name": "引数エラー", "value": "=が多すぎます"})
    errors = check_validation(params, errors)
    if errors:
        embed = discord.Embed(title="hoge", description="fuga", color=0xFF0000)
        embed.title = "ERROR"
        embed.description = "Something is wrong"
        embed.color = 0xFF0000
        for err in errors:
            embed.add_field(name=err["name"], value=err["value"], inline=False)
        await ctx.channel.send(embed=embed)
    else:
        await show_progress_information(ctx, params)


# コマンド処理
async def exec_command(ctx, args):
    if args[1] == "show":
        await show(ctx, args)
    elif args[1] == "check":
        await check(ctx, args)


@client.event
async def on_ready():
    # サーバー起動時に実行
    print("サーバーを起動します。")


@client.event
async def on_message(ctx):
    # Botのメッセージは除外
    if ctx.author.bot:
        return
    # 文字列を空白区切りでリスト化
    args = split_command(ctx.content)
    # /wsmであれば実行
    if args[0] == "/wms":
        await exec_command(ctx, args)


# 実行
client.run(getenv("DISCORD_BOT_TOKEN"))
