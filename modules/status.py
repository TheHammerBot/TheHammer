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
from thehammer.module import Module
import aiohttp
import datetime

class Status(Module):
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
            if entry['name'] == key:
                return entry
        return {}

    @commands.command()
    async def discordstatus(self, ctx):
        INDICATOR_COLORS = {"none":discord.Colour.green(),"partial":discord.Colour.orange(),"major":discord.Colour.red()}
        data = await self.get("https://srhpyqt94yxb.statuspage.io/api/v2/summary.json")
        indicator = data['status']['indicator']
        embed = discord.Embed(color=INDICATOR_COLORS.get(indicator, discord.Colour.blue()), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        embed.add_field(name="API", value=self.get_value(data['components'], "API")['status'].title())
        embed.add_field(name="Gateway", value=self.get_value(data['components'], "Gateway")['status'].title())
        embed.add_field(name="Media Proxy", value=self.get_value(data['components'], "Media Proxy")['status'].title())
        embed.add_field(name="Voice", value=self.get_value(data['components'], "Voice")['status'].title())
        embed.set_footer(text=data['status']['description'])
        return await ctx.send(embed=embed)

def setup(bot):
    bot.load_module(Status)
