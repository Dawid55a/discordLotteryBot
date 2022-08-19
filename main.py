import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiocron

import bot_commands.lottery as lotto
import database

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
bot: discord.ext.commands.Bot = commands.Bot(command_prefix='!',
                                             allowed_mentions=discord.AllowedMentions(everyone=True))


@aiocron.crontab("00 18 * * FRI", start=False)
async def banner_lottery_loop():
    guild: discord.Guild = discord.utils.get(bot.guilds, name=GUILD)
    message_channel = bot.get_channel(int(CHANNEL_ID))

    await message_channel.send("@everyone Lottery is starting...")

    language = await lotto.start_banner_lottery_for(guild=guild)

    await message_channel.send(f"{language} won!")


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
    bot.add_cog(lotto.Lottery(bot, GUILD))
    bot.run(TOKEN)
