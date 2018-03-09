from discord.ext import commands
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
            return await ctx.send(":robot: **Modlog Channel is currently <#{}>**".format(await guild.settings.get("modlog_channel")))
        await guild.update_setting("modlog_channel", channel.id)
        return await ctx.send(":robot: **Modlog Channel updated to <#{}>**".format(channel.id))

def setup(bot):
    bot.add_cog(SettingsModule(bot))
