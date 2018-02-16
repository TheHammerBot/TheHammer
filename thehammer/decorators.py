from discord.ext import commands

def is_owner():
    def check(ctx):
        owners = ctx.bot.config.owners
        return ctx.author.id in owners
    return commands.check(check)