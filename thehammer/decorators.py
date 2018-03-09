from discord.ext import commands

def is_admin_check(ctx):
    if is_owner_check(ctx):
        return True
    admins = ctx.bot.config.admins
    return ctx.author.id in admins
    
def is_owner_check(ctx):
    owners = ctx.bot.config.owners
    return ctx.author.id in owners
    
def is_owner():
    def check(ctx):
        return is_owner_check(ctx)
    return commands.check(check)

def is_admin():
    def check(ctx):
        return is_admin_check(ctx)
    return commands.check(check)

def guild_only():
    def check(ctx):
        return ctx.guild != None
    return commands.check(check)

def is_server_admin():
    def check(ctx):
        if not ctx.guild:
            return False
        if is_admin_check(ctx):
            return True
        if ctx.author.guild_permissions.manage_guild:
            return True
        if ctx.author.guild_permissions.administrator:
            return True
        if ctx.guild.owner.id == ctx.author.id:
            return True
        return False
    return commands.check(check)