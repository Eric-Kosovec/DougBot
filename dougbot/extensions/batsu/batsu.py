import math
import re
from collections import defaultdict

import requests
from nextcord import Embed
from nextcord.ext import commands

from dougbot.common.limits import Limits
from dougbot.extensions.common import embedutils


class Batsu(commands.Cog):

    _SUB_STATUS_PAGE = 'https://www.teamgaki.com/statuspage/'
    _SUB_STATUS_AJAX = 'https://www.teamgaki.com/status/ajax.php'
    _STATUS_LEGEND = 'Not Started > Typesetting > Translating > Quality Check > Prep For Release > Complete!'

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['batsu'])
    async def substatus(self, ctx):
        status_ajax_html = requests.get(self._SUB_STATUS_AJAX).text
        status_page_html = requests.get(self._SUB_STATUS_PAGE).text

        title_re = re.compile(r'<title>(.+?)&#8211;.+?</title>')
        match = title_re.search(status_page_html)
        title = None if match is None else match.group(1)

        menu_item_re = re.compile(r'<li id="menu-item-\d+".+?><a href="(.+?)">')
        games = menu_item_re.findall(status_page_html)
        latest_batsu_game = games[0] if len(games) > 0 else None

        sections_re = re.compile(r'<tr>.*?</tr>')
        completed_re = re.compile(r'Part (\d+) Complete')
        # 3 capture groups of Part, section (minutes), status
        in_progress_re = re.compile(r'<td>(\d+)</td><td>(\d+?\s*?-\s*?\d+?)</td><td.+?>(.+?)</td>')

        status_report = defaultdict(lambda: [])
        for section in sections_re.findall(status_ajax_html):
            completed_match = completed_re.search(section)
            if completed_match is not None:
                status_report[int(completed_match.group(1))].append((completed_match.group(1),))
            else:
                in_progress_match = in_progress_re.search(section)
                if in_progress_match is not None:
                    status_report[int(in_progress_match.group(1))].append((in_progress_match.group(2), in_progress_match.group(3)))

        await self._embed_substatus(ctx, title, status_report, latest_batsu_game)

    async def _embed_substatus(self, ctx, title='Batsu Games', status_report=None, link=None):
        if status_report is None:
            status_report = []

        embed = Embed(title=title, color=0xFF0000, url='' if link is None else link)
        embed.set_footer(text=self._STATUS_LEGEND)

        height = math.ceil(len(status_report) / float(Limits.EMBED_INLINE_FIELD_LIMIT))

        for _ in range(height * Limits.EMBED_INLINE_FIELD_LIMIT):
            embed.add_field(name=embedutils.BLANK_DATA, value=embedutils.BLANK_DATA)

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
                    status_display = embedutils.BLANK_DATA

            embed.set_field_at(r * Limits.EMBED_INLINE_FIELD_LIMIT + c, name=f'Part {i + 1}', value=status_display)

            r = (r + 1) % height
            if r == 0:
                c += 1

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Batsu(bot))
