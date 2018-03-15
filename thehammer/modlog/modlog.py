import discord
import datetime

class Case:
    def __init__(self, bot, guild, data):
        for field in ['case_id', 'type', 'moderator', 'user', 'reason', 'message', 'timestamp']:
            if not field in data:
                raise SyntaxError("Invalid Case")
        self.bot = bot
        self.guild = guild
        self.data = data
    
    def get(self, key, default=None):
        return self.data.get(key, default)

    async def set(self, key, value):
        self.data[key] = value
    
    async def save(self):
        await self.bot.db.cases.update_one({"case_id":self.get("case_id"), "guild_id":self.get("guild_id")}, {"$set":self.data})
        em = await self.generate_embed()
        try:
            message = await self.bot.get_channel(await self.guild.settings.get("modlog_channel", 1)).get_message(self.get("message"))
            await message.edit(embed=em)
        except:
            pass # Pass silently

    async def generate_embed(self):
        em = discord.Embed(title="{} | Case: #{}".format(self.get("type", "Invalid Type"), self.get("case_id", 1)), color=self.get_case_color(self.get("type")), timestamp=self.get("timestamp", None))
        user = await self.bot.get_user_info(self.get("user"))
        try:
            moderator = await self.bot.get_user_info(self.get("moderator"))
        except Exception:
            moderator = None
        if not moderator:
            moderator = "Unknown Moderator"
        em.add_field(name="User", value="{} (<@{}>)".format(str(user), user.id), inline=True)
        em.add_field(name="Moderator", value=str(moderator), inline=True)
        em.add_field(name="Reason", value=self.get("reason"), inline=False)
        em.set_footer(text='ID: {}'.format(user.id))
        return em

    def get_case_color(self, _type):
        if _type.lower() == 'kick' or _type.lower() == 'mute':
            return discord.Colour.gold()
        if _type.lower() == 'ban':
            return discord.Colour.red()
        else:
            return discord.Colour.green()

class ModLog:
    def __init__(self, bot):
        self.bot = bot

    async def get_guild(self, guild):
        return ModGuild(self.bot, guild)

class ModGuild:
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        self.id = guild.id
        self.settings = GuildSettings(bot, self)

    async def generate_global_id(self):
        casecount_doc = await self.bot.db.metadata.find_one({'_id': "case_count"})
        if not casecount_doc:
            await self.bot.db.metadata.insert_one({"_id": "case_count", "value": 0})
            return await self.generate_global_id()
        casecount = casecount_doc['value'] + 1
        await self.bot.db.metadata.replace_one({'_id': "case_count"},{'value': casecount})
        return casecount

    async def generate_id(self):
        casecount = await self.settings.get("latest_case", 0)
        casecount = casecount + 1
        await self.settings.set("latest_case", casecount)
        await self.settings.save()
        return casecount

    async def get_case(self, _id):
        case = await self.bot.db.cases.find_one({"case_id":_id, "guild_id":self.guild.id})
        if not case:
            return None
        case['id'] = _id
        del case['_id']
        return Case(self.bot, self, case)

    async def generate_embed(self, _id, _type, moderator, user, reason, timestamp):
        em = discord.Embed(title="{} | Case: #{}".format(_type, _id), color=self.get_case_color(_type), timestamp=timestamp)
        user = await self.bot.get_user_info(user)
        try:
            moderator = await self.bot.get_user_info(moderator)
        except Exception as e:
            moderator = None
        if not moderator:
            moderator = "Unknown Moderator"
        em.add_field(name="User", value="{} (<@{}>)".format(str(user), user.id), inline=True)
        em.add_field(name="Moderator", value=str(moderator), inline=True)
        em.add_field(name="Reason", value=reason, inline=False)
        em.set_footer(text='ID: {}'.format(user.id))
        return em
    
    async def update_setting(self, key, value):
        await self.settings.set(key, value)
        await self.settings.save()

    def get_case_color(self, _type):
        if _type.lower() == 'kick' or _type.lower() == 'mute':
            return discord.Colour.gold()
        if _type.lower() == 'ban':
            return discord.Colour.red()
        else:
            return discord.Colour.green()

    async def new_case(self, _type, user, moderator, reason=None):
        modlog_channel = await self.settings.get("modlog_channel")
        if not modlog_channel:
            return
        modlog_channel = self.bot.get_channel(modlog_channel)
        if not modlog_channel:
            return
        _id = await self.generate_id()
        if not reason:
            reason = "No reason set, set one with [p]reason {} <reason>".format(_id)
        timestamp = datetime.datetime.utcnow()
        if not moderator:
            moderator = "Unknown Moderator"
        if hasattr(moderator, "id"):
            moderator = moderator.id
        message = await modlog_channel.send(embed=await self.generate_embed(_id, _type, moderator, user.id, reason, timestamp))
        data = {"_id": await self.generate_global_id(), "case_id":_id, "guild_id": self.id, "type": _type, "moderator":moderator, "user":user.id, "reason":reason, "message":message.id, "timestamp":timestamp}
        await self.bot.db.cases.insert_one(data)
        self.bot.logger.info("Created case id {} guild_id {}".format(_id, self.id))
        return Case(self.bot, self, data)

class GuildSettings:
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        self.settings = None

    async def _get_settings(self):
        settings = await self.bot.db.guild_settings.find_one({"_id":self.guild.id})
        if not settings:
            await self.bot.db.guild_settings.insert_one({"_id":self.guild.id})
            settings = {}
        self.settings = settings

    async def set(self, setting, value):
        if not self.settings:
            await self._get_settings()
        self.settings[setting] = value

    async def get(self, setting, default=None):
        if not self.settings:
            await self._get_settings()
        return self.settings.get(setting, default)

    async def save(self):
        if not self.settings:
            return
        await self.bot.db.guild_settings.update_one({"_id":self.guild.id}, {"$set":self.settings})