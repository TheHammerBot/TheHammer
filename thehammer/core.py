import discord
from discord.ext import commands
from thehammer.config import config_from_file
import os
from thehammer.context import CustomContext
import motor.motor_asyncio
from thehammer.modlog import ModLog

class Bot(commands.AutoShardedBot):
    def __init__(self, config_file, logger):
        self.config = config_from_file(config_file)
        self.logger = logger
        super(Bot, self).__init__(command_prefix=self.config.prefix)
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