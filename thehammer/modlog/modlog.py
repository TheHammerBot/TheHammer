import discord

class Case:
    def __init__(self, bot, guild, data):
        for field in ['id', 'type', 'moderator', 'user', 'reason', 'message', 'timestamp']:
            if not field in data:
                raise SyntaxError("Invalid Case")
        self.bot = bot
        self.guild = guild
        self.data = data
    
    async def get(self, key, default=None):
        return self.data.get(key, default)

    async def set(self, key, value):
        self.data[key] = value
    
    async def save(self):
        await self.bot.db.cases.update_one({"_id":self.get("id"), "guild_id":self.get("guild_id")}, {"$set":self.data})
        em = await self.generate_embed()
        try:
            await self.bot.get_message(self.get("message")).edit(embed=em)
        except:
            channel = await self.bot.get_channel(self.guild.settings.get("modlog_channel", None))
            if channel:
                await channel.send(embed=em)

    async def generate_embed(self):
        em = discord.Embed(title="{} | Case: #{}".format(self.get("type", "Invalid Type"), self.get("id", 1)), colour=self.get_case_color(self.get("type")), timestamp=self.get("timestamp", None))
        user = await self.bot.get_user_info(self.get("user"))
        moderator = await self.bot.get_user_info(self.get("moderator"))
        em.add_field(name="User", value="{} (<@{}>)".format(str(user), user.id))
        em.add_field(name="Moderator", value=str(moderator))
        em.add_field(name="Reason", value=self.get("reason"))
        em.set_footer(text='ID: {}'.format(user.id))
        return em

    def get_case_color(self, type):
        if type.lower() in ['kick', 'mute']:
            return discord.Colour.gold()
        if type.lower() in ['ban']:
            return discord.Colour.red()
        else:
            return discord.Colour.green()

class ModLog:
    def __init__(self, bot):
        self.bot = bot

class ModGuild:
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        self.id = guild.id
        self.settings = GuildSettings(bot, self)

    async def generate_id(self):
        casecount_doc = await self.bot.db.metadata.find_one({'_id': "case_count", "guild_id": self.id})
        if not casecount_doc:
            await self.bot.db.metadata.insert_one({"_id": "case_count", "guild_id": self.id, "value": 0})
            return await self.generate_id()
        casecount = casecount_doc['value'] + 1
        await self.bot.db.metadata.replace_one({'_id': "case_count", "guild_id":self.id},{'value': casecount})
        return casecount

    async def get_case(self, id):
        case = await self.bot.db.cases.find({"_id":id, "guild_id":self.guild.id})
        if not case:
            return None
        case['id'] = id
        del case['_id']
        return Case(self.bot, self, case)

    async def new_case(self, type, user, moderator, reason=None):
        modlog_channel = await self.settings.get("modlog_channel")
        if not modlog_channel:
            return
        modlog_channel = self.bot.get_channel(modlog_channel)
        if not modlog_channel:
            return
        _id = await self.generate_id()
        if not reason:
            reason = "No reason set, set one with [p]reason {} <reason>".format(_id)


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