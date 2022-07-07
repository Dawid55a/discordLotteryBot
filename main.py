import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from typing import AnyStr
import datetime
import asyncio

import bot_commands.lottery as lotto
import database

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

USAGE_INFO_FILE: AnyStr = 'usage_info.txt'
bot: discord.ext.commands.Bot = commands.Bot(command_prefix='!')


@tasks.loop(hours=168)
async def banner_lottery_loop():
    guild: discord.Guild = discord.utils.get(bot.guilds, name=GUILD)
    message_channel = bot.get_channel(482274663570079765)

    await message_channel.send("Lottery is starting...")

    language = await lotto.start_banner_lottery_for(guild=guild)

    await message_channel.send(f"{language} won!")


@banner_lottery_loop.before_loop
async def before_banner_lottery_loop():
    for _ in range(60 * 60 * 24 * 7):
        if datetime.datetime.now().strftime("%H:%M %a") == "18:00 Frd":
            print('It is time')
            return
        await asyncio.sleep(30)
        # wait some time before an


@bot.event
async def on_ready():
    guild: discord.Guild = discord.utils.get(bot.guilds, name=GUILD)

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    banner_lottery_loop.start()


if __name__ == '__main__':
    database.init()
    bot.add_cog(lotto.Lottery(bot))
    bot.run(TOKEN)
