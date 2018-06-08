import aiohttp
from thehammer.utils import TimerResetDict
import discord
import datetime

priceEmotes = {
    "vbucks": "<:vbucks:454715357102604298>",
    "vip": "<:vip:454737457167073281>",
    False: ""
}

rarityColors = {
    "common": discord.Colour(0x6e6f72),
    "uncommon": discord.Colour(0x00ac11),
    "rare": discord.Colour(0x0274df),
    "epic": discord.Colour(0x8a12c4),
    "legendary": discord.Colour(0xfb4f04)
}

purple = discord.Colour.purple()

def format_date(date):
    return datetime.datetime.strptime(date[:-5], "%Y-%m-%dT%H:%M:%S")

class FortniteHTTP:
    def __init__(self, bot):
        self.bot = bot
        self.cache = TimerResetDict(bot, "Fortnite.Caches.StatsCache", 10*60)
    
    async def get(self, api_url, headers={}):
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as resp:
                content = await resp.json()
        return content

    async def get_shop(self):
        headers = {'X-API-Key': self.bot.config.fortnite.fnbr}
        url = "https://fnbr.co/api/shop"
        result = await self.get(url, headers)
        result = result['data']
        return FortniteShop(result['daily'], result['featured'], result['date'])

    async def random_cosmetic(self, type):
        url = "https://fnbr.co/api/random?type={type}".format(type=type)
        result = await self.get(url)
        return await self.get_cosmetic(result['item']['name'], type)

    async def get_cosmetic(self, name, type=""):
        headers = {'X-API-Key': self.bot.config.fortnite.fnbr}
        if type != "":
            type = "&type={}".format(type)
        url = "https://fnbr.co/api/images?search={name}{type}".format(name=name, type=type)
        result = await self.get(url, headers)
        result = result['data']
        if len(result) > 0:
            return FortniteCosmetic(**result[0])
        return EmptyFortniteCosmetic()

    async def get_stats(self, username, platform):
        platform = platform.lower()
        if (platform, username) in self.cache:
            result = self.cache[(platform, username)] # Data is still in cache, no need to make a GET request
            return result
        else:
            headers = {"TRN-Api-Key": self.bot.config.fortnite.fortnitetracker}
            url = "https://api.fortnitetracker.com/v1/profile/{platform}/{username}".format(platform=platform, username=username)
            result = await self.get(url, headers=headers)
        if 'error' in result:
            return result['error']
        self.cache[(platform, username)] = result # Put it in the cache
        return result

    async def get_news(self, gamemode):
        url = "https://api.justmaffie.nl/fortnite/news/{gamemode}".format(gamemode=gamemode)
        result = await self.get(url)
        return FortniteNews(result['messages'], result['date'])

class FortniteNews:
    def __init__(self, messages, time):
        self.messages = messages
        self.time = time

    async def send(self, ctx):
        for message in self.messages:
            embed = discord.Embed(color=purple, timestamp=format_date(self.time))
            embed.add_field(name=message['title'], value=message['content'])
            embed.set_thumbnail(url=message['image'])
            await ctx.send(embed=embed)

class FortniteShop:
    def __init__(self, daily, featured, time):
        self.daily = daily
        self.featured = featured
        self.time = time

    async def send(self, ctx):
        featured_items = discord.Embed(color=purple, timestamp=format_date(self.time))
        featured_items.set_author(name="Featured Items")
        featured_items.set_footer(text="Powered by fnbr.co")
        for item in self.featured:
            name = "{name} ({rarity} {type}".format(name=item['name'], rarity=item['rarity'].capitalize(), type=item['readableType'])
            value = "{emote} {price}\n".format(emote=priceEmotes['vbucks'], price=item['price'])
            featured_items.add_field(name=name, value=value)
        daily_items = discord.Embed(color=purple, timestamp=format_date(self.time))
        daily_items.set_author(name="Daily Items")
        daily_items.set_footer(text="Powered by fnbr.co")
        for item in self.daily:
            name = "{name} ({rarity} {type}".format(name=item['name'], rarity=item['rarity'].capitalize(), type=item['readableType'])
            value = "{emote} {price}\n".format(emote=priceEmotes['vbucks'], price=item['price'])
            daily_items.add_field(name=name, value=value)
        await ctx.send(embed=featured_items)
        await ctx.send(embed=daily_items)

class FortniteCosmetic:
    def __init__(self, id, name, price, priceIcon, priceIconLink, images, rarity, type, readableType):
        self.id = id
        self.name = name
        self.price = price
        self.priceIcon = priceIcon
        self.images = images
        self.rarity = rarity
        self.type = type
        self.readableType = readableType

    async def send(self, ctx):
        embed = discord.Embed(color=rarityColors[self.rarity], timestamp=datetime.datetime.utcnow())
        embed.set_author(name=self.name)
        if self.images['gallery']:
            embed.set_image(url=self.images['gallery'])
        else:
            embed.add_field(name="Name", value=self.name)
            price = "{emote} {price}".format(emote=priceEmotes[self.priceIcon], price=self.price)
            embed.add_field(name="Price", value=price)
            embed.add_field(name="Type", value=self.readableType)
            embed.add_field(name="Rarity", value=self.rarity.capitalize())
            embed.set_thumbnail(url=self.images['icon'])
        embed.set_footer(text="Powered by fnbr.co")
        await ctx.send(embed=embed)

class EmptyFortniteCosmetic(FortniteCosmetic):
    def __init__(self):
        super().__init__(None, None, None, None, None, None, None, None, None)

    async def send(self, ctx):
        await ctx.send("This cosmetic could not be found!")