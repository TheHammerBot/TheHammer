from discord.ext import commands
import discord
import platform
from thehammer.decorators import is_server_admin
import datetime

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
            roles.append(role.name)
        embed = discord.Embed(color=discord.Colour.green(), timestamp=datetime.datetime.utcnow())
        author = "{}#{}".format(user.name, user.discriminator)
        username = user.name
        if user.id in self.bot.config.admins:
            username += " <:thehammerdev:422026806464479242>"
        joined_at = member.joined_at
        since_joined = (ctx.message.created_at - joined_at).days
        since_created = (ctx.message.created_at - user.created_at).days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        joined_at = joined_at.strftime("%d %b %Y %H:%M")
        embed.set_author(name=author, icon_url=member.avatar_url)
        embed.add_field(name="ID", value="{}".format(user.id), inline=True)
        embed.add_field(name="Username", value="{}".format(username), inline=True)
        embed.add_field(name="Game", value=member.game, inline=True)
        embed.add_field(name="Roles", value=", ".join(roles))
        embed.add_field(name="Status", value=member.status, inline=True)
        embed.add_field(name="Created At", value="{} (Thats over {} days ago)".format(user_created, since_created), inline=True)
        embed.add_field(name="Joined At", value="{} (Thats over {} days ago)".format(joined_at, since_joined), inline=True)
        embed.set_footer(text='Requested by: {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed)

    @commands.command()
    @is_server_admin()
    async def rolelist(self, ctx):
        buff = ''
        for role in ctx.guild.roles:
            role = '{} - {}\n'.format(role.id, role.name)
            if len(role) + len(buff) > 1990:
                await ctx.channel.send('```{}```'.format(buff))
                buff = ''
            buff += role
        return await ctx.channel.send('```{}```'.format(buff))

    @commands.command(aliases=["info","botinfo"])
    async def about(self, ctx):
        """Get more information about the bot"""
        bot = self.bot
        time1 = datetime.datetime.utcnow()
        msg = await ctx.send("Give me a sec....")
        time2 = datetime.datetime.utcnow()
        if not hasattr(bot, "owner"):
            await msg.edit(content=":robot: **Hey, I'm sorry, but I am not ready yet, please try again in a few seconds.**") # You won't often have to see this, this is only when the bot hasn't yet started up
            return
        embed = discord.Embed(color=discord.Colour.green(), timestamp=datetime.datetime.utcnow())
        discord_version = discord.__version__
        python_version = platform.python_version()
        embed.add_field(name="Discord.py Version", value=discord_version, inline=True)
        embed.add_field(name="Python Version", value=python_version, inline=True)
        embed.add_field(name="Author", value=bot.owner.owner, inline=True)
        embed.add_field(name="Latency", value="{}ms".format(round((time2-time1).total_seconds()*1000)), inline=True)
        embed.add_field(name="Guilds", value=str(len(bot.guilds)), inline=True)
        embed.add_field(name="Users", value=str(len(bot.users)), inline=True)
        if ctx.message.guild:
            embed.add_field(name="Shard ID", value=str(ctx.message.guild.shard_id), inline=True)
        embed.add_field(name="Links", value="**[Guild Invite](https://discord.gg/pfvZCpu)\n[Bot Invite](https://discordapp.com/oauth2/authorize?client_id={}&permissions=8&scope=bot)\n[GitHub](https://github.com/JustMaffie/TheHammer)**".format(self.bot.user.id))
        embed.add_field(name="Developers", value="{}, CircuitRCAY#3038".format(bot.owner.owner))
        embed.set_footer(text='Requested by: {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
        await msg.edit(content=None, embed=embed)


def setup(bot):
    bot.add_cog(InfoModule(bot))
