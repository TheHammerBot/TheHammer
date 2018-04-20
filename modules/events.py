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
from datadog import statsd

class Events:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        bot = self.bot
        game = discord.Game(name="with moderators")
        await bot.change_presence(status=discord.Status.online, activity=game)
        info = [str(self.bot.user), "Discord.py version: {}".format(discord.__version__), 'Shards: {}'.format(self.bot.shard_count), 'Guilds: {}'.format(len(self.bot.guilds)),
            'Users: {}'.format(len(set([m for m in self.bot.get_all_members()]))), '{} modules with {} commands'.format(len(self.bot.cogs), len(self.bot.commands))]
        self.bot.logger.info("")
        for f in info:
            self.bot.logger.info(f)
        self.bot.owner = await self.bot.application_info()

    async def on_message(self, message):
        try:
            if message.guild:
                tags = ["guild:{}".format(message.guild.id),
                        "shard:{}".format(message.guild.shard_id)]
            else:
                tags = []
            statsd.increment(
                'thehammer.messages.count',
                tags=tags
            )
        except BaseException as e:
            self.bot.sentry.captureException()

    async def on_guild_join(self, guild):
        servers = len(self.bot.guilds)
        try:
            statsd.gauge('thehammer.guilds.total', servers)
            statsd.increment('thehammer.guilds.joins',
                             tags=["guild:{}".format(guild.id)])
        except BaseException as e:
            self.bot.sentry.captureException()

    async def on_guild_remove(self, guild):
        servers = len(self.bot.client.guilds)
        try:
            statsd.gauge('thehammer.guilds.total', servers)
            statsd.decrement('thehammer.guilds.joins',
                             tags=["guild:{}".format(guild.id)])
        except BaseException as e:
            self.bot.sentry.captureException()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help()
        elif isinstance(error, commands.BadArgument):
            await ctx.send_help()
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("It looks like this command is disabled.")
        elif isinstance(error, commands.CommandInvokeError):
            self.bot.logger.exception("An error occurred in the command '{}'"
                          "".format(ctx.command.qualified_name), exc_info=error.original)
            message = ("An error occurred in the command ``{}``. Please contact the bot admins ASAP."
                       "".format(ctx.command.qualified_name))
            await ctx.send(message)
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("Hey, I'm sorry, but I can't let you do that!")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("You can't execute this command in Direct Messages!")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send("This command is on cooldown. "
                           "Try again in {:.2f}s"
                           "".format(error.retry_after))
        else:
            self.bot.logger.exception(error)

def setup(bot):
    bot.load_module(Events)
