import os
import discord
from discord.ext import commands
import asyncio
import threading
from flask import Flask

# Flaskアプリのセットアップ
app = Flask(__name__)

@app.route('/')
def home():
    return "Discord Bot with Voting is running!"

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Discord Botのセットアップ
TOKEN = os.getenv("DISCORD_TOKENpick")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 投票コマンドの定義
@bot.command(name='vote')
async def vote(ctx, question: str, duration: str, *options):
    # 時間を "XmYs" 形式で受け取る
    total_seconds = 0
    try:
        if 'm' in duration:
            minutes = int(duration.split('m')[0])
            total_seconds += minutes * 60
            if 's' in duration:
                seconds = int(duration.split('m')[1].replace('s', ''))
                total_seconds += seconds
        elif 's' in duration:
            total_seconds = int(duration.replace('s', ''))
        else:
            await ctx.send("時間の指定が不正です。例: `1m30s` もしくは `90s`")
            return
    except ValueError:
        await ctx.send("時間の形式が正しくありません。例: `1m30s` もしくは `90s`")
        return

    # 選択肢の数チェック
    if len(options) < 2:
        await ctx.send("少なくとも2つの選択肢が必要です！")
        return
    elif len(options) > 10:
        await ctx.send("選択肢は最大10個までです。")
        return

    # 投票メッセージの作成
    description = [f"投票時間は{total_seconds // 60}分{total_seconds % 60}秒です。"]
    for i, option in enumerate(options):
        description.append(f"{i + 1}. {option}")
    embed = discord.Embed(title=f"📊 {question}", description="\n".join(description))
    vote_message = await ctx.send(embed=embed)

    # リアクション（数字）を追加
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    for i in range(len(options)):
        await vote_message.add_reaction(emojis[i])

    # 制限時間の表示
    await ctx.send(f"⏳ 投票は {total_seconds // 60} 分 {total_seconds % 60} 秒間行われます。")

    # 制限時間の待機
    await asyncio.sleep(total_seconds)

    # リアクションの集計
    vote_message = await ctx.channel.fetch_message(vote_message.id)
    reaction_counts = [reaction.count - 1 for reaction in vote_message.reactions[:len(options)]]  # 自分のリアクションを除外

    # 集計結果の表示
    results = []
    for i, count in enumerate(reaction_counts):
        results.append(f"{emojis[i]} {options[i]}: {count}票")

    result_embed = discord.Embed(title="📊 投票結果", description="\n".join(results))
    await ctx.send(embed=result_embed)

# Discord BotとFlaskを並行して実行するための関数
def run_discord_bot():
    bot.run(TOKEN)

# FlaskとDiscord Botを同時に実行するためのスレッドを作成
if __name__ == "__main__":
    # Flaskを別スレッドで実行
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Discord Botをメインスレッドで実行
    run_discord_bot()
