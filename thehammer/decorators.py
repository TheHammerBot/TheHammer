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

def is_server_admin_check(ctx):
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

def has_role(ctx, id):
    role = discord.utils.get(ctx.author.roles, id=id)
    return role is not None

def is_server_admin():
    def check(ctx):
        return is_server_admin_check(ctx)
    return commands.check(check)

async def is_server_mod_check(ctx):
    if not ctx.guild:
        return False
    if is_admin_check(ctx):
        return True
    if is_server_admin_check(ctx):
        return True
    guild = await ctx.bot.modlog.get_guild(ctx.guild)
    for role in await guild.settings.get("mod_roles", []):
        if has_role(ctx, role):
            return True
    for user in await guild.settings.get("mod_users", []):
        if ctx.author.id == user:
            return True
    return False

def is_server_mod():
    async def check(ctx):
        return await is_server_mod_check(ctx)
    return commands.check(check)