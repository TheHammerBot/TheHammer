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
import datetime
from thehammer.module import Module

class Random(Module):
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

    @commands.command()
    async def password(self, ctx):
        pwd = str(uuid.uuid4()).replace("-", "")
        await ctx.author.send("Here is your random password: `{}`".format(pwd))
        return await ctx.send("{} I've sent you a new password in DM".format(ctx.author.mention))

    @commands.command()
    async def trbmb(self, ctx):
        await ctx.trigger_typing()
        quote = await self.get("http://api.chew.pro/trbmb")
        return await ctx.channel.send(quote[0])

    @commands.command()
    async def whatdoestrumpthink(self, ctx):
        await ctx.trigger_typing()
        quote = await self.get("https://api.whatdoestrumpthink.com/api/v1/quotes/random")
        return await ctx.channel.send(quote['message'])

    @commands.command()
    async def dog(self, ctx):
        await ctx.trigger_typing()
        dog = await self.get("https://dog.ceo/api/breeds/image/random")
        embed = discord.Embed(color=discord.Colour.blue(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_image(url=dog['message'])
        return await ctx.send(embed=embed)

    @commands.command()
    async def cat(self, ctx):
        await ctx.trigger_typing()
        cat = await self.get("https://aws.random.cat/meow")
        embed = discord.Embed(color=discord.Colour.blue(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_image(url=cat['file'])
        return await ctx.send(embed=embed)

    @commands.command()
    async def duck(self, ctx):
        await ctx.trigger_typing()
        duck = await self.get("https://random-d.uk/api/v1/random?type=jpg")
        embed = discord.Embed(color=discord.Colour.blue(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_image(url=duck['url'])
        embed.set_footer(text=duck['message'])
        return await ctx.send(embed=embed)

    @commands.command()
    async def coffee(self, ctx):
        await ctx.trigger_typing()
        coffee = await self.get("https://coffee.alexflipnote.xyz/random.json")
        embed = discord.Embed(color=discord.Colour.blue(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_image(url=coffee['file'])
        return await ctx.send(embed=embed)

    @commands.command()
    async def joke(self, ctx):
        await ctx.trigger_typing()
        joke = await self.get("http://api.icndb.com/jokes/random?firstName=&lastName={}".format(ctx.author.name))
        return await ctx.channel.send(joke['value']['joke'])

    @commands.command()
    async def catfact(self, ctx):
        await ctx.trigger_typing()
        fact = await self.get("https://catfact.ninja/fact")
        return await ctx.channel.send(fact['fact'])

def setup(bot):
    bot.load_module(Random)
