from discord.ext import commands
import discord

class ModLogModule:
    def __init__(self, bot):
        self.bot = bot

module = None

def setup(bot):
    module = ModLogModule(bot)
    bot.add_cog(module)
