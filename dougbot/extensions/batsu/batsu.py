from requests_html import AsyncHTMLSession, HTMLResponse, HTML

from discord.ext import commands


class Batsu(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sub_status(self, ctx):
        link = 'https://teamgaki.com/status'
        session = AsyncHTMLSession()
        response = HTMLResponse._from_response(session.get(link))
        response.html.render()
        print(response.html)
        print(response.text)

def setup(bot):
    bot.add_cog(Batsu(bot))
