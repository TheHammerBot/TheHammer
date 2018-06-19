import aiohttp
from thehammer.utils import TimerResetDict
import discord
import datetime
from math import ceil
from io import BytesIO
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import base64
from imgurpython import ImgurClient
import os

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
        self.daily_image = TimerResetDict(bot, "Fortnite.Caches.DailyShopCache", 30*60)
        self.imgur = ImgurClient(self.bot.config.imgur.client_id, self.bot.config.imgur.client_secret)

    async def upload_image(self, path, name="file.png"):
        result = self.imgur.upload_from_path(path, {"name":name})
        return result

    async def get(self, api_url, headers={}):
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as resp:
                content = await resp.json()
        return content

    async def post(self, api_url, data={}, headers={}):
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, data=data, headers=headers) as resp:
                content = await resp.json()
        return content

    async def get_shop(self):
        headers = {'X-API-Key': self.bot.config.fortnite.fnbr}
        url = "https://fnbr.co/api/shop"
        result = await self.get(url, headers)
        return result.get('data',{})

    async def get_shop_embed(self):
        result = await self.get_shop()
        return FortniteShop(result['daily'], result['featured'], result['date'])

    async def get_shop_image(self):
        result = await self.get_shop()
        return FortniteShopImage(self, result)

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
        url = "https://api.justmaffie.nl/api/v1/fortnite/news/{gamemode}".format(gamemode=gamemode)
        result = await self.get(url, headers={"X-API-Key":self.bot.config.fortnite.justmaffie})
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

class FortniteShopImage: # created by @Douile https://github.com/Douile
    def __init__(self, http, result):
        self.http = http
        self.daily = result.get('daily',[])
        self.featured = result.get('featured',[])
        self.date = result['date']
        self.rowsize = 4
        self.itemsize = 200
        self.padding = 20
        self.IMAGENAME = 'generatedshopimage.png'

    async def send(self, ctx):
        if "image" in self.http.daily_image:
            image = self.http.daily_image['image']
            embed = discord.Embed(timestamp=format_date(self.date), colour=discord.Color.purple())
            embed.set_author(name="Fortnite Shop")
            embed.set_image(url=image)
            return await ctx.send(embed=embed)
        image = await self.generate()
        image.save("tmp/daily.png", "PNG")
        result = await self.http.upload_image("tmp/daily.png", self.IMAGENAME)
        os.remove("tmp/daily.png")
        self.http.daily_image['image'] = result['link']
        embed = discord.Embed(timestamp=format_date(self.date), colour=discord.Color.purple())
        embed.set_author(name="Fortnite Shop")
        embed.set_image(url=result['link'])
        return await ctx.send(embed=embed)

    async def generate(self):
        items = self.featured + self.daily
        rows = ceil(len(items) / self.rowsize)
        width = round(self.padding*(self.rowsize+1)+self.itemsize*self.rowsize)
        height = round(self.padding*(rows+1)+self.itemsize*rows)
        background = PIL.Image.new('RGBA',(width,height),(0,0,0,0))
        row_array = await self.split_rows(items, self.rowsize)

        left = self.padding
        top = self.padding
        for row in row_array:
            for item in row:
                url = item.get('images',{}).get('gallery')
                if url:
                    image = await self.retrieve_image(url,self.itemsize)
                    background.paste(image,(left,top),image)
                left += self.itemsize + self.padding
            top += self.itemsize + self.padding
            left = self.padding
        return background

    async def split_rows(self, items,rowsize):
        rows = []
        for i in range(0,len(items),rowsize):
            rows.append(items[i:i+rowsize])
        return rows

    async def retrieve_image(self, url,size):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                bytes = await response.read()
        image = PIL.Image.open(BytesIO(bytes)).convert('RGBA')
        return image.resize((size,size))


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
