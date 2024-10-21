import discord
from discord.ext import commands
from collections import defaultdict
import asyncio
from datetime import timedelta
import os
import threading
from flask import Flask

intents = discord.Intents.default()
intents.messages = True  # メッセージイベントを有効化
intents.guilds = True
intents.message_content = True  # メッセージ内容を取得

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("DISCORD_TOKENcombo")

# ユーザーごとのメッセージ履歴を保持するための辞書
message_history = defaultdict(list)

# 設定: 許可するメッセージの数と時間（秒）
MESSAGE_LIMIT = 5
TIME_LIMIT = 10  # 秒数
TIMEOUT_DURATION = 10  # タイムアウトの秒数

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  # メッセージ履歴に現在のメッセージのタイムスタンプを追加
  message_history[message.author.id].append(message.created_at)

  # 古いメッセージを削除
  while message_history[message.author.id] and (message.created_at - message_history[message.author.id][0]).total_seconds() > TIME_LIMIT:
    message_history[message.author.id].pop(0)

  # 連投制限のチェック
  if len(message_history[message.author.id]) > MESSAGE_LIMIT:
    # ユーザーをタイムアウト
    await message.author.timeout(timedelta(seconds=TIMEOUT_DURATION))
    await message.channel.send(f"{message.author.mention} さん、連投を達成しました！次元の彼方に飛ばしました。")
    message_history[message.author.id].clear()  # メッセージ履歴をクリア

  await bot.process_commands(message)

app = Flask(__name__)

@app.route('/')
def home():
  return "Discord Bot is running!"

def run_flask():
  app.run(host='0.0.0.0', port=5000)

def run_discord_bot():
  bot.run(TOKEN)

# FlaskとDiscord Botを同時に実行するためのスレッドを作成
if __name__ == "__main__":
  # Flaskを新しいスレッドで起動
  flask_thread = threading.Thread(target=run_flask)
  flask_thread.start()

  # Discord Botをメインスレッドで起動
  run_discord_bot()
