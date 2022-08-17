import random
import sqlite3
from typing import AnyStr, ByteString, List

import discord
from discord.ext import commands

import database


# from main import bot, GUILD


async def clear_votes():
    database.conn.execute('''
    DELETE FROM user_votes WHERE TRUE;
    ''')


async def reset_used_languages():
    database.conn.execute('''
    UPDATE language_image_usage SET
        used = 0
    WHERE TRUE;
    ''')


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
    await clear_votes()

    used_percent = database.conn.execute('''
    SELECT COUNT(*)*1.0/(SELECT COUNT(*) FROM language_image_usage) 
    FROM language_image_usage
    WHERE used = 0;
    ''').fetchone()
    if used_percent[0] < 0.5:
        await reset_used_languages()

    return chosen_language

async def show_votes(ctx: discord.ext.commands.context.Context):
    vote: str
    vote_data = database.conn.execute('''SELECT username,voted_language FROM user_votes;''').fetchall()
    if not vote_data:
        await ctx.send(f"No one has votes yet. Be the first!")
    else:
        message = '\n'.join([f"{name:<20} voted {vote.capitalize()}" for name, vote in vote_data])
        message = "```\n" + message + "\n```"
        await ctx.send(message)
        print("Voting list showed")
    return

async def show_languages(ctx: discord.ext.commands.context.Context):
    languages = database.conn.execute(
        '''SELECT language FROM language_image_usage GROUP BY language;''').fetchall()
    message = '\n'.join([f"{i} {lang[0]}" for i, lang in enumerate(languages)])
    message = "```\n" + message + "\n```"
    await ctx.send(message)
    print("Languages list showed")
    return

class Lottery(commands.Cog):
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild

    @commands.command()
    async def start_lottery(self, ctx: discord.ext.commands.context.Context):
        """Starts lottery countdown"""
        await ctx.send("Lottery is starting...")
        guild: discord.Guild = discord.utils.get(self.bot.guilds, name="X'Gon Give It 2 Ya")

        language = await start_banner_lottery_for(guild=guild)

        await ctx.send(f"{language} won!")

    @commands.command()
    async def vote(self, ctx: discord.ext.commands.context.Context) -> None:
        """Give your vote on language of your choosing
            !vote {language}
        """
        msg: AnyStr = ctx.message.content

        if msg != (str(ctx.prefix) + str(ctx.command)):

            voted_language: str = msg.split(maxsplit=1)[1].rstrip()
            languages = database.conn.execute('''
            SELECT language FROM language_image_usage
            WHERE 1==1
            GROUP BY language;
            ''').fetchall()
            languages = [lang.lower() for lang in list(next(zip(*languages)))]

            if voted_language.lower() in languages:
                try:
                    database.conn.execute('''
                    INSERT INTO user_votes (username, voted_language, vote_date) VALUES (?, ?, ?);
                    ''', [str(ctx.author), voted_language.lower(),
                          ctx.message.created_at.strftime("%Y/%m/%d %H:%M:%S")])

                    database.conn.execute('''
                    UPDATE language_image_usage SET
                        weight = weight + 100
                    WHERE language = ?;
                    ''', [voted_language.lower()])
                    database.conn.commit()
                    await ctx.send(f"{ctx.author} voted on {voted_language}")
                except sqlite3.IntegrityError:
                    await ctx.send("You already voted! No take backs")
                finally:
                    print(f"{ctx.author} Voted")
                return

        await ctx.send(f"Incorrect command")


    @commands.command(brief="Show votes or languages")
    async def show(self, ctx: discord.ext.commands.context.Context):
        """Show:
                > votes: list containing voter and voted language
                > languages: list of possible programming languages
        """
        msg: AnyStr = ctx.message.content
        vote: str
        msg_split = msg.split()
        if msg != (str(ctx.prefix) + str(ctx.command)) and len(msg_split) == 2:
            option = msg_split[1]
            if option == "votes":
                await show_votes(ctx)
            elif option == "languages":
                await show_languages(ctx)
            else:
                await ctx.send(f"Incorrect command. Available options (votes | languages)")
        else:
            await ctx.send(f"Wrong amount of arguments. !show (votes | languages)")
            
