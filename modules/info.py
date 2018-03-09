from discord.ext import commands
import discord
import platform
import asyncio

class InfoModule:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def userinfo(self, ctx, user:discord.User=None):
        """Grab information about a user"""
        if not ctx.message.guild:
            return await ctx.send("You can only execute this command in a guild")
        guild = ctx.message.guild
        if not user:
            user = ctx.author
        member = guild.get_member(user.id)
        _roles = member.roles
        roles = []
        for role in _roles:
            roles.append(role.name.replace("@here", "[at]here").replace("@everyone", "[at]everyone"))
        embed = discord.Embed(color=discord.Colour.green())
        embed.title = "{}#{}".format(user.name, user.discriminator)
        if user.id in self.bot.config.admins:
            embed.title += " <:thehammerdev:414012044862423040>"
        joined_at = member.joined_at
        since_joined = (ctx.message.created_at - joined_at).days
        since_created = (ctx.message.created_at - user.created_at).days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        joined_at = joined_at.strftime("%d %b %Y %H:%M")
        embed.add_field(name="ID", value="{}".format(user.id), inline=True)
        embed.add_field(name="Username", value="{}".format(user.name), inline=True)
        embed.add_field(name="Game", value=member.game, inline=True)
        embed.add_field(name="Roles", value=", ".join(roles))
        embed.add_field(name="Status", value=member.status, inline=True)
        embed.add_field(name="Created At", value="{} (Thats over {} days ago)".format(user_created, since_created), inline=True)
        embed.add_field(name="Joined At", value="{} (Thats over {} days ago)".format(joined_at, since_joined), inline=True)
        return await ctx.send(embed=embed)

    @commands.command(aliases=["info","botinfo"])
    async def about(self, ctx):
        """Get more information about the bot"""
        bot = self.bot
        if not hasattr(bot, "owner"):
            return await ctx.send("Hey, I'm sorry, but I am not ready yet, please try again in a few seconds.") # You won't often have to see this, this is only when the bot hasn't yet started up
        embed = discord.Embed(color=discord.Colour.green())
        discord_version = discord.__version__
        python_version = platform.python_version()
        mongo_status = "Available"
        try:
            await asyncio.wait_for(asyncio.ensure_future(bot.mongo.admin.command("ismaster"), loop=self.bot.loop), 1, loop=self.bot.loop)
        except:
            mongo_status = "Offline"
        embed.add_field(name="Discord.py Version", value=discord_version, inline=True)
        embed.add_field(name="Python Version", value=python_version, inline=True)
        embed.add_field(name="Author", value=bot.owner.owner, inline=True)
        embed.add_field(name="Latency", value=str(round(bot.latency, 3)), inline=True)
        embed.add_field(name="Guilds", value=str(len(bot.guilds)), inline=True)
        embed.add_field(name="Users", value=str(len(bot.users)), inline=True)
        if ctx.message.guild:
            embed.add_field(name="Shard ID", value=str(ctx.message.guild.shard_id), inline=True)
        embed.add_field(name="Database", value="**MongoDB:** {}".format(mongo_status), inline=True)
        embed.add_field(name="Links", value="**[Guild Invite](soontm)\n"
                                            "[Bot Invite](https://discordapp.com/oauth2/authorize?client_id={}&permissions=8&scope=bot)**".format(self.bot.user.id))
        embed.add_field(name="Developers", value="{}, CircuitRCAY#3038".format(bot.owner.owner))
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(InfoModule(bot))
