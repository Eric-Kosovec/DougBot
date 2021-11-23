import mimetypes
import os
from functools import partial
from http.server import CGIHTTPRequestHandler

from discord.ext import commands

from dougbot.common.webserver import WebServer
from dougbot.core.bot import DougBot
from dougbot.extensions.common.annotations.admincheck import admin_command
from dougbot.extensions.common.sanitize import sanitize_url


# Instantiated per request
class BingoHandler(CGIHTTPRequestHandler):
    def __init__(self, web_base, *args, **kwargs):
        self._web_base = web_base
        super().__init__(*args, directory=self._web_base, **kwargs)

    def do_GET(self):
        page_path = sanitize_url(self.path)
        if page_path == '/' or page_path.endswith('index.html'):
            page_path = os.path.join(self._web_base, 'index.html')
        else:
            page_path = os.path.join(self._web_base, self.path[1:])

        if not os.path.exists(page_path):
            self.send_response(404)
            self.end_headers()
            return

        with open(page_path, 'rb') as fd:
            page = fd.read()

        self.send_response(200)
        self.send_header("Content-type", mimetypes.guess_type(page_path))
        self.end_headers()

        self.wfile.write(page)

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        self.do_GET()


class Bingo(commands.Cog):

    def __init__(self, bot: DougBot):
        self.bot = bot
        self._web_server = None
        self._web_base = os.path.join(bot.RESOURCES_DIR, 'extensions', 'bingo', 'www/')

    @commands.command()
    @commands.guild_only()
    @admin_command()
    async def bingo_server(self, ctx):
        if self._web_server is None:
            self._web_server = WebServer(('', 8080), partial(BingoHandler, self._web_base))
            self._web_server.serve_forever()
            print(self._web_server.server_address)
        #await ctx.send(f'http://localhost:8080')

    @commands.command()
    @commands.guild_only()
    @admin_command()
    async def stop_bingo(self, _):
        if self._web_server is not None:
            self._web_server.shutdown()


def setup(bot):
    bot.add_cog(Bingo(bot))
