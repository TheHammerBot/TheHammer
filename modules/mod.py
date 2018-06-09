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

from thehammer.context import CustomContext
from thehammer.decorators import is_server_mod
import datetime
from thehammer.module import Module

class Mod(Module):
    def __init__(self, bot):
        self.bot = bot
        self.ban_queue = []
        self.kick_queue = []

    @commands.command()
    @is_server_mod()
    async def kick(self, ctx, user:discord.Member, *, reason:str=None):
        is_special = ctx.author == ctx.guild.owner
        if not ctx.guild.get_member(ctx.bot.user.id).guild_permissions.kick_members and not ctx.guild.get_member(ctx.bot.user.id).guild_permissions.administrator:
            return await ctx.send("Hey, I can't do that, please ask an administrator to give me KICK_MEMBERS or ADMINISTRATOR permission!")
        if ctx.author.top_role.position > user.top_role.position or is_special:
            guild = await self.bot.modlog.get_guild(ctx.guild)
            self.kick_queue.append((guild.id, user.id))
            await user.kick(reason="[{moderator}] {reason}".format(moderator=str(ctx.author), reason=reason))
            _type = "Kick"
            moderator = ctx.author
            await guild.new_case(_type, user, moderator, reason)
            return await ctx.send("Kicked user <@{}> for {}!".format(user.id, reason))
        else:
            return await ctx.send("Hey, I'm sorry, but that user is higher in the hierarchy than you are, I can't let you do that...")

    @commands.command()
    @is_server_mod()
    async def ban(self, ctx, user:discord.Member, *, reason:str=None):
        is_special = ctx.author == ctx.guild.owner
        if not ctx.guild.get_member(ctx.bot.user.id).guild_permissions.ban_members and not ctx.guild.get_member(ctx.bot.user.id).guild_permissions.administrator:
            return await ctx.send("Hey, I can't do that, please ask an administrator to give me BAN_MEMBERS or ADMINISTRATOR permission!")
        if ctx.author.top_role.position > user.top_role.position or is_special:
            guild = await self.bot.modlog.get_guild(ctx.guild)
            self.ban_queue.append((guild.id, user.id))
            await user.ban(reason="[{moderator}] {reason}".format(moderator=str(ctx.author), reason=reason))
            _type = "Ban"
            moderator = ctx.author
            await guild.new_case(_type, user, moderator, reason)
            return await ctx.send("Banned user <@{}> for {}!".format(user.id, reason))
        else:
            return await ctx.send("Hey, I'm sorry, but that user is higher in the hierarchy than you are, I can't let you do that...")

    @commands.command()
    @is_server_mod()
    async def hackban(self, ctx, _id: int, *, reason: str=None):
        is_special = ctx.author == ctx.guild.owner
        bot = self.bot
        user = ctx.guild.get_member(_id)
        if user is not None:
            return await ctx.invoke(self.ban, user=user)
        try:
            guild = await self.bot.modlog.get_guild(ctx.guild)
            user = await bot.get_user_info(_id)
            await bot.http.ban(_id, guild.id, 0)
            _type = "Hackban"
            moderator = ctx.author
            await guild.new_case(_type, user, moderator, reason)
            await ctx.send("Hackbanned user with the id {} for {}!".format(_id, reason))
        except discord.NotFound:
            await ctx.send("I'm sorry, this ID is invalid. Can't really ban a person that doesn't exist, right?")
        except discord.Forbidden:
            await ctx.send("I'm sorry, I can't ban this user, not enough permissions?")

    @commands.command()
    @is_server_mod()
    async def mute(self, ctx, user:discord.Member, *, reason:str=None):
        is_special = ctx.author == ctx.guild.owner
        if not ctx.guild.get_member(ctx.bot.user.id).guild_permissions.manage_roles and not ctx.guild.get_member(ctx.bot.user.id).guild_permissions.administrator:
            return await ctx.send("Hey, I can't do that, please ask an administrator to give me MANAGE_ROLES or ADMINISTRATOR permission!")
        if ctx.author.top_role.position > user.top_role.position or is_special:
            guild = await self.bot.modlog.get_guild(ctx.guild)
            mutedrole = await guild.settings.get("muted_role", None)
            if not mutedrole:
                return await ctx.send("There is not currently a muted role set!")
            mutedrole = discord.utils.get(guild.guild.roles, id=mutedrole)
            if not mutedrole:
                return await ctx.send("The configured muted role is invalid, has it been deleted?")
            if mutedrole in user.roles:
                return await ctx.send("This user is already muted!")
            await user.add_roles(mutedrole, reason="[{moderator}] {reason}".format(moderator=str(ctx.author), reason=reason), atomic=True)
            _type = "Mute"
            moderator = ctx.author
            await guild.new_case(_type, user, moderator, reason)
            return await ctx.send("Muted user <@{}> for {}!".format(user.id, reason))
        else:
            return await ctx.send("Hey, I'm sorry, but that user is higher in the hierarchy than you are, I can't let you do that...")

    async def on_member_ban(self, guild, user):
        if (guild.id, user.id) in self.ban_queue:
            self.ban_queue.remove((guild.id, user.id))
            return
        try:
            guild = await self.bot.modlog.get_guild(guild)
            async for entry in guild.guild.audit_logs(action=discord.AuditLogAction.ban):
                if not entry.user.id == guild.guild.me.id:
                    if entry.target.id == user.id:
                        return await guild.new_case("Ban", entry.target, entry.user, entry.reason)
        except discord.Forbidden:
            pass
        except Exception as e:
            self.bot.logger.exception("An error occurred", exc_info=e)

    async def on_member_remove(self, member):
        if (member.guild.id, member.id) in self.kick_queue:
            self.kick_queue.remove((member.guild.id, member.id))
            return
        try:
            guild = await self.bot.modlog.get_guild(member.guild)
            ban = discord.utils.get(await guild.guild.bans(), user=member)
            if ban:
                return
            async for entry in guild.guild.audit_logs(action=discord.AuditLogAction.kick, after=(datetime.datetime.utcnow() - datetime.timedelta(seconds=60))):
                if not entry.user.id == guild.guild.me.id:
                    if entry.target.id == member.id:
                        return await guild.new_case("Kick", entry.target, entry.user, entry.reason)
        except discord.Forbidden:
            pass
        except Exception as e:
            self.bot.logger.exception("An error occurred", exc_info=e)

    @commands.command()
    @is_server_mod()
    async def unmute(self, ctx, user:discord.Member, *, reason:str=None):
        is_special = ctx.author == ctx.guild.owner
        if not ctx.guild.get_member(ctx.bot.user.id).guild_permissions.manage_roles and not ctx.guild.get_member(ctx.bot.user.id).guild_permissions.administrator:
            return await ctx.send("Hey, I can't do that, please ask an administrator to give me MANAGE_ROLES or ADMINISTRATOR permission!")
        if ctx.author.top_role.position > user.top_role.position or is_special:
            guild = await self.bot.modlog.get_guild(ctx.guild)
            mutedrole = await guild.settings.get("muted_role", None)
            if not mutedrole:
                return await ctx.send("There is not currently a muted role set!")
            mutedrole = discord.utils.get(guild.guild.roles, id=mutedrole)
            if not mutedrole:
                return await ctx.send("The configured muted role is invalid, has it been deleted?")
            if not mutedrole in user.roles:
                return await ctx.send("This user is not muted!")
            await user.remove_roles(mutedrole, reason="[{moderator}] {reason}".format(moderator=str(ctx.author), reason=reason), atomic=True)
            _type = "Unmute"
            moderator = ctx.author
            await guild.new_case(_type, user, moderator, reason)
            return await ctx.send("Unmuted user <@{}> for {}!".format(user.id, reason))
        else:
            return await ctx.send("Hey, I'm sorry, but that user is higher in the hierarchy than you are, I can't let you do that...")

    @commands.command()
    @is_server_mod()
    async def reason(self, ctx, case:int, *, reason:str):
        guild = await self.bot.modlog.get_guild(ctx.guild)
        case = await guild.get_case(case)
        if not case:
            return await ctx.send("That case doesn't exist!")
        await case.set("reason", reason)
        await case.set("moderator", ctx.author.id)
        await case.save()
        return await ctx.send("Reason Updated!")

def setup(bot):
    bot.load_module(Mod)
