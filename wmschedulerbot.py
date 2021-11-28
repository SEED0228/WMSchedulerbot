import discord
import json
from os import getenv
from datetime import datetime as dt

from infrastructure.apiclient import apiClient

# オブジェクトを取得
discordClient = discord.Client()

# 文字列を空白区切りでリスト化
def split_command(content):
    args = content.replace("　", " ").split(" ")
    while "" in args:
        args.remove("")
    return args


def check_validation(params, errors):
    return errors


async def show_event_information(ctx, params: dict):
    r = apiClient.fetch_events(params)
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
    r = apiClient.fetch_event_progresses(params)
    status = {
        0: "todo",
        1: "doing",
        2: "done",
    }
    status_emoji = {
        0: ":green_square:",
        1: ":arrows_counterclockwise:",
        2: ":white_check_mark:",
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
                name=f"{status_emoji[progress['status']]}:{progress['event']['title']}",
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
    usernames = {
        "SEED": "seed",
        "I.TK": "itk",
        "Liberal": "liberal",
    }
    params = {
        "from_deadline": dt.now().strftime("%Y%m%d"),
        "username": usernames[ctx.author.name],
    }
    errors = []
    for arg in args[2:]:
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


async def add(ctx, args):
    status = {
        "todo": "0",
        "doing": "1",
        "done": "2",
        "0": "0",
        "1": "1",
        "2": "2",
    }
    status_str = {
        "0": "todo",
        "1": "doing",
        "2": "done",
    }
    usernames = {
        "SEED": "seed",
        "I.TK": "itk",
        "Liberal": "liberal",
    }
    if args[3] in status:
        params = {
            "uid": args[2] + "@wsdmoodle.waseda.jp",
            "username": usernames[ctx.author.name],
            "status": status[args[3]],
        }
        r = apiClient.create_and_update_event_progresses(params)
        if r.status_code == 201:
            embed = discord.Embed(
                title=f"登録成功({params['username']})",
                description=f"{params['uid'][:-20]} {status_str[params['status']]}",
                color=0x00FF00,
            )
        else:
            embed = discord.Embed(title="ERROR", description="", color=0xFF0000)
            data = json.loads(r.text)
            for atr in data:
                for err in data[atr]:
                    embed.add_field(name=atr, value=err, inline=False)
    else:
        embed = discord.Embed(title="引数エラー", description="ステータス名が不正です", color=0xFF0000)
    await ctx.channel.send(embed=embed)


# コマンド処理
async def exec_command(ctx, args):
    if args[1] == "show":
        await show(ctx, args)
    elif args[1] == "check":
        await check(ctx, args)
    elif args[1] == "add" or args[1] == "update":
        await add(ctx, args)


@discordClient.event
async def on_ready():
    # サーバー起動時に実行
    print("サーバーを起動します。")


@discordClient.event
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
def main():
    discordClient.run(getenv("DISCORD_BOT_TOKEN"))


if __name__ == "__main__":
    main()
