import discord
import os
import threading
from discord.ext import commands
from datetime import timedelta  # これが必要です
from flask import Flask


intents = discord.Intents.default()
intents.messages = True  # メッセージをキャッチするためのintent
intents.guilds = True
intents.members = True  # メンバー情報にアクセスするためのintent
intents.message_content = True

TOKEN = os.getenv("DISCORD_TOKENng")

bot = commands.Bot(command_prefix='!', intents=intents)

# 初期状態のNGワードリスト
NG_WORDS = ["spam", "offensive", "badword"]  # 初期のNGワードをここに設定

# NGワードを追加するコマンド
@bot.command(name='add_ngword')
@commands.has_permissions(administrator=True)  # 管理者権限をチェック
async def add_ngword(ctx, word: str):
  word = word.lower()
  if word not in NG_WORDS:
    NG_WORDS.append(word)
    await ctx.send(f"NGワード '{word}' が追加されたぞ！。")
  else:
    await ctx.send(f"'{word}' は既にNGワードに登録されている!。")

# NGワードを削除するコマンド
@bot.command(name='remove_ngword')
@commands.has_permissions(administrator=True)  # 管理者権限をチェック
async def remove_ngword(ctx, word: str):
  word = word.lower()
  if word in NG_WORDS:
    NG_WORDS.remove(word)
    await ctx.send(f"NGワード '{word}' が削除されてしまった。")
  else:
    await ctx.send(f"'{word}' はNGワードに存在しない。")

# メッセージが送信された際にNGワードをチェックする
@bot.event
async def on_message(message):
  # Bot自身のメッセージを無視する
  if message.author.bot:
    return

  # NGワードがメッセージに含まれているかチェック
  for word in NG_WORDS:
    if word in message.content.lower():
      try:
        # タイムアウト処理: ここでは10分（600秒）
        timeout_duration = timedelta(minutes=1)
        await message.author.timeout(timeout_duration)
        await message.channel.send(f"{message.author.mention} はNGワード '{word}' を言ってしまったので次元の彼方に飛ばされました。")
      except discord.errors.Forbidden:
        await message.channel.send("タイムアウトの権限がありません。")
      break  #

  # コマンドの処理もon_messageで行いたい場合
  await bot.process_commands(message)

# Flaskアプリのセットアップ
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
