from discord.ext import commands


class CustomContext(commands.Context):
    async def send_help(self):
        command = self.invoked_subcommand or self.command
        pages = await self.bot.formatter.format_help_for(self, command)
        ret = []
        for page in pages:
            ret.append(await super().send(page))
        return ret

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
    	if content:
    		content = ":robot: **{}**".format(content)
    	return await super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)