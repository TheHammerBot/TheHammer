from discord.ext import commands
import discord
import discord
from thehammer.decorators import is_server_admin

class SettingsModule:
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
            return await ctx.send(":robot: **Modlog Channel is currently <#{}>!**".format(await guild.settings.get("modlog_channel")))
        await guild.update_setting("modlog_channel", channel.id)
        return await ctx.send(":robot: **Modlog Channel updated to <#{}>!**".format(channel.id))

    @settings.command()
    @is_server_admin()
    async def mutedrole(self, ctx, role:int=None):
        guild = await self.bot.modlog.get_guild(ctx.guild)
        if not role:
            mutedrole = await guild.settings.get("muted_role")
            role = discord.utils.get(guild.guild.roles, id=mutedrole)
            if not role:
                return await ctx.send(":robot: **There is no valid muted role set!**")
            return await ctx.send(":robot: **The muted role is currently set to {}!**".format(role.name))
        role = discord.utils.get(guild.guild.roles, id=role)
        if not role:
            return await ctx.send(":robot: **I can't seem to find that role!**")
        if guild.guild.default_role.id == role.id:
            return await ctx.send(":robot: **The [at]everyone role cannot be a muted role!**")
        guild = await self.bot.modlog.get_guild(guild)
        muted_role = await guild.settings.get("muted_role", None)
        role = role.id
        if role == muted_role:
            return await ctx.send(":robot: **That role is already the muted role!**")

        await guild.update_setting("muted_role", role)
        await guild.settings.save()
        return await ctx.send(":robot: **That role is now the muted role!**")

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
            return await ctx.send(":robot: **Please enter the role ID!**")
        role = discord.utils.get(guild.roles, id=role)
        if not role:
            return await ctx.send(":robot: **I can't seem to find that role!**")
        if guild.default_role.id == role.id:
            return await ctx.send(":robot: **The [at]everyone role cannot be a moderator role!**")
        guild = await self.bot.modlog.get_guild(guild)
        roles = await guild.settings.get("mod_roles", [])
        role = role.id
        if role in roles:
            return await ctx.send(":robot: **That role is already a moderator role!**")
        roles.append(role)
        await guild.update_setting("mod_roles", roles)
        return await ctx.send(":robot: **Added the role to the moderators list!**")

    @mods.command()
    @is_server_admin()
    async def listroles(self, ctx):
        guild = await self.bot.modlog.get_guild(ctx.guild)
        roles = await guild.settings.get("mod_roles", [])
        if len(roles) < 1:
            return await ctx.send(":robot: **There are no moderator roles!**")
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
            return await ctx.send(":robot: **Please enter the role ID!**")
        guild = await self.bot.modlog.get_guild(guild)
        roles = await guild.settings.get("mod_roles", [])
        role = role.id
        if not role in roles:
            return await ctx.send(":robot: **That role is not moderator role!**")
        roles.remove(role)
        await guild.update_setting("mod_roles", roles)
        return await ctx.send(":robot: **Removed the role from the moderators list!**")

    @mods.command()
    @is_server_admin()
    async def adduser(self, ctx, user:discord.Member=None):
        guild = ctx.guild
        if not user:
            return await ctx.send(":robot: **Please mention the user!**")
        guild = await self.bot.modlog.get_guild(guild)
        users = await guild.settings.get("mod_users", [])
        if user.id in users:
            return await ctx.send(":robot: **That user is already a moderator!**")
        users.append(user.id)
        await guild.update_setting("mod_users", users)
        return await ctx.send(":robot: **Added the user to the moderators list!**")

    @mods.command()
    @is_server_admin()
    async def listusers(self, ctx):
        guild = await self.bot.modlog.get_guild(ctx.guild)
        users = await guild.settings.get("mod_users", [])
        if len(users) < 1:
            return await ctx.send(":robot: **There are no moderator users!**")
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
            return await ctx.send(":robot: **Please mention the user!**")
        guild = await self.bot.modlog.get_guild(guild)
        users = await guild.settings.get("mod_users", [])
        if not user.id in users:
            return await ctx.send(":robot: **That user is not moderator!**")
        users.remove(user.id)
        await guild.update_setting("mod_users", users)
        return await ctx.send(":robot: **Removed the user from the moderators list!**")

def setup(bot):
    bot.add_cog(SettingsModule(bot))
