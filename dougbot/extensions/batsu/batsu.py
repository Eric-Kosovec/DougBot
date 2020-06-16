import math
import re
from collections import defaultdict

import requests
from discord import Embed
from discord.ext import commands

from dougbot.common import limits


class Batsu(commands.Cog):

    _SUB_STATUS_URL = 'https://www.teamgaki.com/status/ajax.php'

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['batsu', 'gaki'])
    async def substatus(self, ctx):
        page = requests.get(self._SUB_STATUS_URL).text

        sections_re = r'<tr>.*?</tr>'
        completed_re = re.compile(r'Part (\d+) Complete')
        # 3 capture groups of Part, section (minutes), status
        in_progress_re = re.compile(r'<td>(\d+)</td><td>(\d+?\s*?-\s*?\d+?)</td><td.+?>(.+?)</td>')

        status_report = defaultdict(lambda: [])
        for section in re.findall(sections_re, page):
            completed_match = completed_re.search(section)
            if completed_match is not None:
                status_report[int(completed_match.group(1))].append((f'Part {int(completed_match.group(1))} Complete!',))
            else:
                in_progress_match = in_progress_re.search(section)
                if in_progress_match is not None:
                    status_report[int(in_progress_match.group(1))].append((in_progress_match.group(2), in_progress_match.group(3)))

        await self._embed_substatus(ctx, status_report)

    @staticmethod
    async def _embed_substatus(ctx, status_report):
        legend = 'Not Started > Typesetting > Translating > Quality/English Check > Prep For Release > Complete!'
        embed = Embed(title='Batsu Games Subbing Status', description=legend, color=0xFF0000)

        height = math.ceil(len(status_report) / float(limits.EMBED_INLINE_FIELD_LIMIT))

        for _ in range(height * limits.EMBED_INLINE_FIELD_LIMIT):
            embed.add_field(name='\u200b', value='\u200b')

        r = 0
        c = 0
        for i in range(len(status_report)):
            if len(status_report[i + 1][0]) == 1:
                status_display = 'Complete!'
            else:
                status_display = ''
                for time, status in status_report[i + 1]:
                    status_display += f'{time} | {status}\n'
                if len(status_display) == 0:
                    status_display = '\u200b'

            embed.set_field_at(r * limits.EMBED_INLINE_FIELD_LIMIT + c, name=f'Part {i + 1}', value=status_display)

            r = (r + 1) % height
            if r == 0:
                c += 1

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Batsu(bot))
