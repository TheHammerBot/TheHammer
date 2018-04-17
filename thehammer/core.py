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

import discord
from discord.ext import commands
from thehammer.config import config_from_file
import os
from thehammer.context import CustomContext
import motor.motor_asyncio
from thehammer.modlog import ModLog

async def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(bot.config.prefix)
    guild = await bot.modlog.get_guild(message.guild)
    return commands.when_mentioned_or(await guild.settings.get("command_prefix", bot.config.prefix))(bot, message)

class Bot(commands.AutoShardedBot):
    def __init__(self, config_file, logger):
        self.config = config_from_file(config_file)
        self.logger = logger
        super(Bot, self).__init__(command_prefix=get_prefix)
        self.init_databases()
        self.modlog = ModLog(self)

    async def get_context(self, message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)

    def run_bot(self):
        self.load_all_extensions()
        token = self.config.token
        self.run(token)

    def init_databases(self):
        self.init_mongo()

    def load_extension(self, name):
        self.logger.info('LOADING EXTENSION {name}'.format(name=name))
        if not name.startswith("modules."):
            name = "modules.{}".format(name)
        return super().load_extension(name)

    def unload_extension(self, name):
        self.logger.info('UNLOADING EXTENSION {name}'.format(name=name))
        if not name.startswith("modules."):
            name = "modules.{}".format(name)
        return super().unload_extension(name)

    def load_all_extensions(self):
        _modules = [os.path.splitext(x)[0] for x in os.listdir("modules")]
        modules = []
        for module in _modules:
            if not module.startswith("_"):
                modules.append("modules.{}".format(module))

        for module in modules:
            self.load_extension(module)

    def init_mongo(self):
        self.mongo = motor.motor_asyncio.AsyncIOMotorClient(self.config.mongo.url, io_loop=self.loop)
        self.db = self.mongo[self.config.mongo.dbname]

    def shutdown(self):
        self.mongo.close()
        self.logout()

    def run(self, *args, **kwargs):
        loop = self.loop
        try:
            loop.run_until_complete(self.start(*args, **kwargs))
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()

def make_bot(logger):
    config_file = "config.json"
    bot = Bot(config_file, logger)
    return bot