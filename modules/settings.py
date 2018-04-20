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
import discord
from thehammer.decorators import is_server_admin

class Settings:
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @is_server_admin()
    async def settings(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @settings.command()
    @is_server_admin()
    async def modlog(self, ctx, channel:discord.TextChannel=None):
        guild = await self.bot.modlog.get_guild(ctx.guild)
        if not channel:
            return await ctx.send("Modlog Channel is currently <#{}>!".format(await guild.settings.get("modlog_channel")))
        await guild.update_setting("modlog_channel", channel.id)
        return await ctx.send("Modlog Channel updated to <#{}>!".format(channel.id))

    @settings.command()
    @is_server_admin()
    async def prefix(self, ctx, prefix):
        guild = await self.bot.modlog.get_guild(ctx.guild)
        if not prefix:
            return await ctx.send("Prefix is currently set to {}!".format(await guild.settings.get("command_prefix", self.bot.config.prefix)))
        await guild.update_setting("command_prefix", prefix)
        return await ctx.send("Prefix updated to {}!".format(prefix))

    @settings.command()
    @is_server_admin()
    async def mutedrole(self, ctx, role:int=None):
        guild = await self.bot.modlog.get_guild(ctx.guild)
        if not role:
            mutedrole = await guild.settings.get("muted_role")
            role = discord.utils.get(guild.guild.roles, id=mutedrole)
            if not role:
                return await ctx.send("There is no valid muted role set!")
            return await ctx.send("The muted role is currently set to {}!".format(role.name))
        role = discord.utils.get(guild.guild.roles, id=role)
        if not role:
            return await ctx.send("I can't seem to find that role!")
        if guild.guild.default_role.id == role.id:
            return await ctx.send("The [at]everyone role cannot be a muted role!")
        muted_role = await guild.settings.get("muted_role", None)
        role = role.id
        if role == muted_role:
            return await ctx.send("That role is already the muted role!")
        await guild.update_setting("muted_role", role)
        await guild.settings.save()
        return await ctx.send("That role is now the muted role!")

    @settings.command()
    @is_server_admin()
    async def createmutedrole(self, ctx):
        guild = await self.bot.modlog.get_guild(ctx.guild)
        mutedrole = await guild.settings.get("muted_role")
        role = discord.utils.get(guild.guild.roles, id=mutedrole)
        if role:
            return await ctx.send("There is already a valid muted role set!")
        role = guild.guild.default_role
        if not role:
            # Its unlikely
            return await ctx.send("Huh?! This guild doesn't have a default role?!")
        permissions = role.permissions
        permissions.update(create_instant_invite=False, add_reactions=False, send_messages=False, send_tts_messages=False)
        role = await guild.guild.create_role(name="Muted", permissions=permissions, colour=discord.Colour.darker_grey(), hoist=False, mentionable=False, reason="Automatic creation of muted role")
        categories = []
        textchannels = []
        for channel in guild.guild.channels:
            if isinstance(channel, discord.CategoryChannel):
                categories.append(channel)
            elif isinstance(channel, discord.TextChannel):
                textchannels.append(channel)
        for cat in categories:
            await cat.set_permissions(role, create_instant_invite=False, add_reactions=False, send_messages=False, send_tts_messages=False)
        for channel in textchannels:
            await channel.set_permissions(role, create_instant_invite=False, add_reactions=False, send_messages=False, send_tts_messages=False)
        await guild.update_setting("muted_role", role.id)
        return await ctx.send("Created a muted role!")

    @commands.group()
    @is_server_admin()
    async def mods(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @mods.command()
    @is_server_admin()
    async def addrole(self, ctx, role:int=None):
        guild = ctx.guild
        if not role:
            return await ctx.send("Please enter the role ID!")
        role = discord.utils.get(guild.roles, id=role)
        if not role:
            return await ctx.send("I can't seem to find that role!")
        if guild.default_role.id == role.id:
            return await ctx.send("The [at]everyone role cannot be a moderator role!")
        guild = await self.bot.modlog.get_guild(guild)
        roles = await guild.settings.get("mod_roles", [])
        role = role.id
        if role in roles:
            return await ctx.send("That role is already a moderator role!")
        roles.append(role)
        await guild.update_setting("mod_roles", roles)
        return await ctx.send("Added the role to the moderators list!")

    @mods.command()
    @is_server_admin()
    async def listroles(self, ctx):
        guild = await self.bot.modlog.get_guild(ctx.guild)
        roles = await guild.settings.get("mod_roles", [])
        if len(roles) < 1:
            return await ctx.send("There are no moderator roles!")
        actualRoles = []
        for role in roles:
            role = discord.utils.get(guild.guild.roles, id=role)
            if role:
                actualRoles.append(role)

        buff = ''
        for role in actualRoles:
            role = '**{}**\n'.format(role.name)
            if len(role) + len(buff) > 1990:
                await ctx.send('{}'.format(buff))
                buff = ''
            buff += role
        return await ctx.send('{}'.format(buff))

    @mods.command()
    @is_server_admin()
    async def removerole(self, ctx, role:int=None):
        guild = ctx.guild
        if not role:
            return await ctx.send("Please enter the role ID!")
        guild = await self.bot.modlog.get_guild(guild)
        roles = await guild.settings.get("mod_roles", [])
        role = role.id
        if not role in roles:
            return await ctx.send("That role is not moderator role!")
        roles.remove(role)
        await guild.update_setting("mod_roles", roles)
        return await ctx.send("Removed the role from the moderators list!")

    @mods.command()
    @is_server_admin()
    async def adduser(self, ctx, user:discord.Member=None):
        guild = ctx.guild
        if not user:
            return await ctx.send("Please mention the user!")
        guild = await self.bot.modlog.get_guild(guild)
        users = await guild.settings.get("mod_users", [])
        if user.id in users:
            return await ctx.send("That user is already a moderator!")
        users.append(user.id)
        await guild.update_setting("mod_users", users)
        return await ctx.send("Added the user to the moderators list!")

    @mods.command()
    @is_server_admin()
    async def listusers(self, ctx):
        guild = await self.bot.modlog.get_guild(ctx.guild)
        users = await guild.settings.get("mod_users", [])
        if len(users) < 1:
            return await ctx.send("There are no moderator users!")
        actualUsers = []
        for user in users:
            user = guild.guild.get_member(user)
            if user:
                actualUsers.append(user)

        buff = ''
        for user in actualUsers:
            user = '**{}**\n'.format(str(user))
            if len(user) + len(buff) > 1990:
                await ctx.send('{}'.format(buff))
                buff = ''
            buff += user
        return await ctx.send('{}'.format(buff))

    @mods.command()
    @is_server_admin()
    async def removeuser(self, ctx, user:discord.Member=None):
        guild = ctx.guild
        if not user:
            return await ctx.send("Please mention the user!")
        guild = await self.bot.modlog.get_guild(guild)
        users = await guild.settings.get("mod_users", [])
        if not user.id in users:
            return await ctx.send("That user is not moderator!")
        users.remove(user.id)
        await guild.update_setting("mod_users", users)
        return await ctx.send("Removed the user from the moderators list!")

def setup(bot):
    bot.load_module(Settings)
