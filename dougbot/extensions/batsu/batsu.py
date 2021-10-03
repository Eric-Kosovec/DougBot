import math
import re
from collections import defaultdict

import requests
from discord import Embed
from discord.ext import commands

from dougbot.common.limits import Limits


class Batsu(commands.Cog):

    _SUB_STATUS_PAGE = 'https://www.teamgaki.com/statuspage/'
    _SUB_STATUS = 'https://www.teamgaki.com/status/ajax.php'

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['batsu', 'gaki'])
    async def substatus(self, ctx):
        status_html = requests.get(self._SUB_STATUS).text
        status_page_html = requests.get(self._SUB_STATUS_PAGE).text

        menu_item_re = re.compile(r'<li id="menu-item-\d+".+?><a href="(.+?)">.+?</a></li>')
        games = re.findall(menu_item_re, status_page_html)
        latest_batsu_game = games[0] if len(games) > 0 else None

        sections_re = r'<tr>.*?</tr>'
        completed_re = re.compile(r'Part (\d+) Complete')
        # 3 capture groups of Part, section (minutes), status
        in_progress_re = re.compile(r'<td>(\d+)</td><td>(\d+?\s*?-\s*?\d+?)</td><td.+?>(.+?)</td>')

        status_report = defaultdict(lambda: [])
        for section in re.findall(sections_re, status_html):
            completed_match = completed_re.search(section)
            if completed_match is not None:
                status_report[int(completed_match.group(1))].append((f'Part {int(completed_match.group(1))} Complete!',))
            else:
                in_progress_match = in_progress_re.search(section)
                if in_progress_match is not None:
                    status_report[int(in_progress_match.group(1))].append((in_progress_match.group(2), in_progress_match.group(3)))

        await self._embed_substatus(ctx, status_report, latest_batsu_game)

    @staticmethod
    async def _embed_substatus(ctx, status_report, link=None):
        blank_data = '\u200b'
        legend = 'Not Started > Typesetting > Translating > Quality/English Check > Prep For Release > Complete!'
        embed = Embed(title='Batsu Games Subbing Status', description=legend, color=0xFF0000)

        if link is not None:
            embed.url = link

        height = math.ceil(len(status_report) / float(Limits.EMBED_INLINE_FIELD_LIMIT))

        for _ in range(height * Limits.EMBED_INLINE_FIELD_LIMIT):
            embed.add_field(name=blank_data, value=blank_data)

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
                    status_display = blank_data

            embed.set_field_at(r * Limits.EMBED_INLINE_FIELD_LIMIT + c, name=f'Part {i + 1}', value=status_display)

            r = (r + 1) % height
            if r == 0:
                c += 1

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Batsu(bot))
