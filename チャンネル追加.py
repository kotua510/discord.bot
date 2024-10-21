import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True  # コマンドのメッセージを処理するためのインテント


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

bot.run('')
