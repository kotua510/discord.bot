import os
import threading
import discord
from discord.ext import commands
from flask import Flask


intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True  # コマンドのメッセージを処理するためのインテント

TOKEN = os.getenv("DISCORD_TOKENchanel")


bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def create_channels(ctx, *channel_names):
  """複数のチャンネル名を指定してチャンネルを作成します。"""
  if not channel_names:
    await ctx.send("チャンネル名を指定してください。")
    return

  for channel_name in channel_names:
    channel = await ctx.guild.create_text_channel(channel_name)
    await ctx.send(f"チャンネル {channel.name} を作成しました。")


@create_channels.error
async def create_channels_error(ctx, error):
  if isinstance(error, commands.BadArgument):
    await ctx.send("無効な引数です。正しい形式で指定してください。")
  elif isinstance(error, commands.MissingPermissions):
    await ctx.send("チャンネルを作成する権限がありません。")

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
