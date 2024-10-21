import os
import threading
import discord
from discord.ext import commands
from flask import Flask

# Discord Botのセットアップ
TOKEN = os.getenv("DISCORD_TOKENvc")

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
  print(f'Bot {bot.user.name} is ready.')

@bot.event
async def on_voice_state_update(member, before, after):
  # サーバー内の特定のテキストチャンネルを取得（例: "general"）
  guild = member.guild
  text_channel = discord.utils.get(guild.text_channels, name="一般")

  if text_channel is not None:
    if before.channel is None and after.channel is not None:
      # ユーザーがボイスチャンネルに参加した場合
      await text_channel.send(f'{member.display_name} が {after.channel.name} に登場しました！')

    elif before.channel is not None and after.channel is None:
      # ユーザーがボイスチャンネルから退出した場合
      await text_channel.send(f'{member.display_name} が {before.channel.name} を退場しました！')

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
