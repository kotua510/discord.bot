import os
import threading
import discord
from discord.ext import commands
from flask import Flask

intents = discord.Intents.default()
intents.guilds = True
intents.members = True  # メンバーにアクセスするためのインテント
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.getenv("DISCORD_TOKENlore")

# 色の指定用の辞書（色名と色コードの対応）
COLOR_CODES = {
    "red": discord.Color.red(),
    "blue": discord.Color.blue(),
    "green": discord.Color.green(),
    "yellow": discord.Color.yellow(),
    "purple": discord.Color.purple(),
    # 必要に応じて他の色も追加可能
}

@bot.command()
@commands.has_permissions(manage_roles=True)
async def assign_roles(ctx, *user_role_color_admin_pairs):
  """ユーザーに指定されたロールと色を付与し、管理者権限を設定します。ロールが存在しない場合は作成します。"""
  if len(user_role_color_admin_pairs) % 4 != 0:
    await ctx.send("ユーザー、ロール、色、管理者権限を正しくペアにしてください。")
    return

  for i in range(0, len(user_role_color_admin_pairs), 4):
    user_mention = user_role_color_admin_pairs[i]
    role_name = user_role_color_admin_pairs[i + 1]
    color_name = user_role_color_admin_pairs[i + 2]
    admin_status = user_role_color_admin_pairs[i + 3].lower()

    # メンバーを取得
    member = ctx.guild.get_member_named(user_mention)
    if member is None:
      await ctx.send(f"ユーザー {user_mention} が見つかりません。")
      continue

    # ロールを取得、存在しなければ作成
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
      # 色を指定
      color = COLOR_CODES.get(color_name.lower(), discord.Color.default())
      # 管理者権限を付与するかどうかを判断
      is_admin = admin_status == "true"
      role = await ctx.guild.create_role(
          name=role_name,
          permissions=discord.Permissions(
              administrator=is_admin),  # 管理者権限を付与
          color=color
      )
      await ctx.send(f"ロール {role_name} を作成（管理者: {is_admin}）。")

    # ユーザーにロールを付与
    await member.add_roles(role)
    await ctx.send(f"{user_mention} にロール {role_name} を付与完了。")

@assign_roles.error
async def assign_roles_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("ロールを管理する権限がありません。")
  elif isinstance(error, commands.BadArgument):
    await ctx.send("無効な引数です。正しい形式で指定してください。")

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
