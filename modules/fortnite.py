"""
    The Hammer
    Copyright (C) 2018 JustMaffie

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from discord.ext import commands
import discord
import aiohttp
import datetime
from thehammer.module import Module
from thehammer.modules.fortnite import FortniteHTTP
import random

class Fortnite(Module):
    def __init__(self, bot):
        self.bot = bot
        self.http = FortniteHTTP(bot)

    def get_value(self, list, key):
        for entry in list:
            if entry['key'] == key:
                return entry
        return {}

    async def generate_embed(self, author, data):
        embed = discord.Embed(colour=discord.Colour.blue(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name="Platform", value=data['platformNameLong'])
        embed.add_field(name="Username", value=data['epicUserHandle'])
        stats = data['lifeTimeStats']
        embed.add_field(name="Wins", value=str(self.get_value(stats, "Wins")['value']))
        embed.add_field(name="Matches Played", value=str(self.get_value(stats, "Matches Played")['value']))
        embed.add_field(name="Win Percentage", value=str(self.get_value(stats, "Win%")['value']))
        embed.add_field(name="Kills", value=str(self.get_value(stats, "Kills")['value']))
        embed.add_field(name="Kill/Death Ratio", value=str(self.get_value(stats, "K/d")['value']))
        embed.set_footer(text='Requested by: {}'.format(author), icon_url=author.avatar_url)
        return embed

    @commands.group()
    async def fortnite(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help()
    
    @fortnite.command()
    async def shop(self, ctx):
        shop = await self.http.get_shop()
        await shop.send(ctx)

    @fortnite.command()
    async def cosmetic(self, ctx, *, name):
        cosmetic = await self.http.get_cosmetic(name)
        await cosmetic.send(ctx)

    @fortnite.command()
    async def stats(self, ctx, platform:str, *, username):
        if not hasattr(self.bot, "owner"):
            return await ctx.send("Hey, I'm sorry, but I am not ready yet, please try again in a few seconds.") # You won't often have to see this, this is only when the bot hasn't yet started up
        stats = await self.http.get_stats(username, platform)
        if isinstance(stats, str):
            return await ctx.send("{error}".format(error=stats))
        return await ctx.send(embed=await self.generate_embed(ctx.author, stats))

    @fortnite.command()
    async def random(self, ctx, type=None):
        types = ['backpack', 'glider', 'pickaxe', 'skin', 'loading', 'outfit']
        if not type:
            type = random.choice(types)
        type = type.lower()
        nice_types = [type.capitalize() for type in types]
        if not type in types:
            return await ctx.send("Invalid type, valid types are: `{types}`".format(types="`, `".join(nice_types)))
        if type == "skin":
            type = "outfit"
        cosmetic = await self.http.random_cosmetic(type)
        await cosmetic.send(ctx)

    @fortnite.command()
    async def news(self, ctx, *, gamemode=None):
        nice_gamemodes = ["BR", "Battle Royale", "STW", "Save The World"]
        if not gamemode:
            return await ctx.send("Invalid gamemode, valid gamemodes are: `{gamemodes}`".format(gamemodes="`, `".join(nice_gamemodes)))
        gamemodes = ['br', 'battle royale', 'stw', 'save the world']
        gamemode = gamemode.lower()
        if not gamemode in gamemodes:
            return await ctx.send("Invalid gamemode, valid gamemodes are: `{gamemodes}`".format(gamemodes="`, `".join(nice_gamemodes)))
        if gamemode == "br" or gamemode == "battle royale":
            gamemode = "battleroyale"
        else:
            gamemode = "savetheworld"
        news = await self.http.get_news(gamemode)
        await news.send(ctx)

def setup(bot):
    bot.load_module(Fortnite)
