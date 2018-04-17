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