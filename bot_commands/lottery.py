import random
import sqlite3
from typing import AnyStr, ByteString, List

import discord
from discord.ext import commands

import database


async def find_random_image(language: AnyStr) -> ByteString:
    images: List = database.conn.execute('''
    SELECT l.image FROM language_image_usage as l
    WHERE language = (?) AND used = 0;
    ''', [language]).fetchall()

    banner_image: AnyStr = random.choice(images)[0]

    print(f"Chosen Image: {banner_image}")

    database.conn.execute('''
    UPDATE language_image_usage
    SET
        weight = weight,
        used = 1
    WHERE image = :img ;
    ''', {"img": banner_image})

    database.conn.commit()

    with open(f"Anime-Girls-Holding-Programming-Books-master/{language}/{banner_image}", 'rb') as image:
        banner = image.read()
    return banner


async def start_banner_lottery_for(guild: discord.Guild) -> AnyStr:
    languages_weighted = database.conn.execute('''
    SELECT l.language, l.weight FROM language_image_usage as l
    WHERE l.used == 0
    GROUP BY l.language;
    ''').fetchall()

    languages, weight = zip(*languages_weighted)

    chosen_language: AnyStr = random.choices(population=languages,
                                             weights=weight,
                                             k=1)[0]

    print(f"Chosen Language: {chosen_language}")

    banner = await find_random_image(chosen_language)
    await guild.edit(banner=banner)
    print("Banner changed")
    return chosen_language


class Lottery(commands.Cog):
    # def __init__(self, bot):
    #     self.bot = bot

    @commands.command()
    async def start_lottery(self, ctx: discord.ext.commands.context.Context):
        """Starts lottery countdown"""
        await ctx.send("Lottery is starting...")
        guild: discord.Guild = discord.utils.get(bot.guilds, name=GUILD)

        language = await start_banner_lottery_for(guild=guild)

        await ctx.send(f"{language} won!")

    @commands.command()
    async def vote(self, ctx: discord.ext.commands.context.Context) -> None:
        """Give your vote on language of your choosing
            !vote {language}
        """
        msg: AnyStr = ctx.message.content

        if msg != (str(ctx.prefix) + str(ctx.command)):

            voted_language = msg.split()[1:]
            languages = database.conn.execute('''
            SELECT language FROM language_image_usage
            WHERE 1==1
            GROUP BY language;
            ''').fetchall()
            languages = [lang.lower() for lang in list(next(zip(*languages)))]

            if voted_language[0].lower() in languages:
                try:
                    database.conn.execute('''
                    INSERT INTO user_votes (username, voted_language, vote_date) VALUES (?, ?, ?);
                    ''', [str(ctx.author), voted_language[0], ctx.message.created_at.strftime("%Y/%m/%d %H:%M:%S")])

                    database.conn.execute('''
                    UPDATE language_image_usage SET
                        weight = weight + 100
                    WHERE language = ?;
                    ''', [voted_language[0].lower()])
                    database.conn.commit()
                    await ctx.send(f"{ctx.author} voted on {voted_language[0]}")
                except sqlite3.IntegrityError:
                    await ctx.send("You already voted! No take backs")
                finally:
                    print(f"{ctx.author} Voted")
                return

        await ctx.send(f"Incorrect command")

    @commands.command()
    async def show_votes(self, ctx: discord.ext.commands.context.Context):
        """Show list containing voter and voted language"""
        msg: AnyStr = ctx.message.content

        if msg == (str(ctx.prefix) + str(ctx.command)):
            vote_data = database.conn.execute('''SELECT username,voted_language FROM user_votes;''').fetchall()
            message = '\n'.join([f"{name:<20} voted {vote}" for name, vote in vote_data])
            message = "```" + message + "```"
            await ctx.send(message)
            print("Voting list showed")
            return
        await ctx.send(f"Incorrect command")

    @commands.command()
    async def show_languages(self, ctx: discord.ext.commands.context.Context):
        """Show list of possible programing languages"""
        msg: AnyStr = ctx.message.content

        if msg == (str(ctx.prefix) + str(ctx.command)):
            languages = database.conn.execute(
                '''SELECT language FROM language_image_usage GROUP BY language;''').fetchall()
            message = '\n'.join([f"{i} {lang[0]}" for i, lang in enumerate(languages)])
            message = "```" + message + "```"
            await ctx.send(message)
            print("Languages list showed")
            return
        await ctx.send(f"Incorrect command")
