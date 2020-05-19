import re
from collections import defaultdict

import requests
from discord.ext import commands


class Batsu(commands.Cog):

    _SUB_STATUS_URL = 'https://www.teamgaki.com/status/ajax.php'

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
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

        await self._display_substatus(ctx, status_report)

    @staticmethod
    async def _display_substatus(ctx, status_report):
        legend = 'Not Started > Typesetting > Translating > Quality/English Check > Prep For Release > Complete!'
        substatus = f'{legend}\n\n'

        # Status report comes in form {Part #: [(Complete,), (Section String, Status)]}

        for i in range(1, len(status_report) + 1):
            for section in status_report[i]:
                if len(section) == 1:
                    substatus += f'{section[0]}\n'
                elif len(section) == 2:
                    substatus += f'Part {i}\tSection {section[0]}\tStatus {section[1]}\n'
        await ctx.send(substatus)


def setup(bot):
    bot.add_cog(Batsu(bot))
