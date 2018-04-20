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
from thehammer.utils import TimerResetDict
import datetime
from thehammer.module import Module

class Fortnite(Module):
    def __init__(self, bot):
        self.bot = bot
        self.cache = TimerResetDict(10*60)

    async def get_session(self):
        if not hasattr(self, "session"):
            self.session = aiohttp.ClientSession()
        return self.session

    async def get(self, api_url, headers={}):
        session = await self.get_session()
        resp = await session.get(api_url, headers=headers)
        content = await resp.json()
        resp.close()
        return content

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

    @commands.command()
    async def fortnite(self, ctx, platform:str, *, username):
        if not hasattr(self.bot, "owner"):
            return await ctx.send(":robot: **Hey, I'm sorry, but I am not ready yet, please try again in a few seconds.**") # You won't often have to see this, this is only when the bot hasn't yet started up
        platform = platform.lower()
        if (platform, username) in self.cache:
            result = self.cache[(platform, username)] # Data is still in cache, no need to make a GET request
        else:
            result = await self.get("https://api.fortnitetracker.com/v1/profile/{platform}/{username}".format(platform=platform, username=username), headers={"TRN-Api-Key": self.bot.config.fortnite_api_key})
        self.cache[(platform, username)] = result # Put it in the cache
        if 'error' in result:
            return await ctx.send("{error}".format(error=result['error']))
        return await ctx.send(embed=await self.generate_embed(ctx.author, result))

def setup(bot):
    bot.load_module(Fortnite)
