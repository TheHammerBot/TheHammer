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
import uuid
import os

class RandomModule:
    def __init__(self, bot):
        self.bot = bot

    async def get_session(self):
        if not hasattr(self, "session"):
            self.session = aiohttp.ClientSession()
        return self.session

    async def get(self, api_url):
        session = await self.get_session()
        resp = await session.get(api_url)
        content = await resp.json()
        resp.close()
        return content

    async def get_file(self, file_url):
        session = await self.get_session()
        resp = await session.get(file_url)
        data = await resp.read()
        resp.close()
        return data

    @commands.command()
    async def password(self, ctx):
        pwd = str(uuid.uuid4()).replace("-", "")
        await ctx.author.send("Here is your random password: `{}`".format(pwd))
        return await ctx.send("{} I've sent you a new password in DM".format(ctx.author.mention))

    @commands.command()
    async def trbmb(self, ctx):
        await ctx.trigger_typing()
        quote = await self.get("http://api.chew.pro/trbmb")
        return await ctx.send("``{}``".format(quote[0]))

    @commands.command()
    async def whatdoestrumpthink(self, ctx):
        await ctx.trigger_typing()
        quote = await self.get("https://api.whatdoestrumpthink.com/api/v1/quotes/random")
        return await ctx.send("``{}``".format(quote['message']))

    @commands.command()
    async def dog(self, ctx):
        await ctx.trigger_typing()
        dog = await self.get("https://dog.ceo/api/breeds/image/random")
        img = await self.get_file(dog['message'])
        file = discord.File(img, "dog.png")
        return await ctx.send(file=file)

    @commands.command()
    async def cat(self, ctx):
        await ctx.trigger_typing()
        cat = await self.get("https://aws.random.cat/meow")
        img = await self.get_file(cat['file'])
        file = discord.File(img, "cat.{}".format(os.path.splitext(cat['file'])[1]))
        return await ctx.send(file=file)

    @commands.command()
    async def duck(self, ctx):
        await ctx.trigger_typing()
        duck = await self.get("https://random-d.uk/api/v1/random?type=jpg")
        img = await self.get_file(duck['url'])
        file = discord.File(img, "duck.png")
        return await ctx.send(file=file)

def setup(bot):
    bot.add_cog(RandomModule(bot))