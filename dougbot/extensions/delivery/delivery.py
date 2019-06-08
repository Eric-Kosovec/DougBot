import os
import subprocess

from discord.ext import commands
from discord.ext.commands.errors import *

from dougbot.extensions.util.admin_check import admin_command


class Delivery(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=False)
    @admin_command()
    async def restart(self, ctx):
        _ = ctx
        await self._restart_bot()

    @commands.command()
    @admin_command()
    async def update(self, ctx):
        await self._update(ctx, ['git', 'pull'])

    @commands.command()
    @admin_command()
    async def force_update(self, ctx):
        await self._update(ctx, ['git', 'fetch', '--all'], ['git', 'reset', '--hard', 'origin/master'])

    @commands.command()
    @admin_command()
    async def update_dependencies(self, ctx):
        await self._update(ctx, ['python', os.path.join(self.bot.ROOT_DIR, 'update_deps.py')])

    async def _update(self, ctx, *cmds):
        if ctx is None or cmds is None:
            return

        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)

        # Find which files will change - core files or extensions
        # Extensions can be reloaded, core files require restarting
        changed = subprocess.check_output(['git', 'diff', '--name-only'])
        changed = str(changed, 'utf-8').split('\n')

        reload_extensions = []
        restart_bot = False
        for changed_file in changed:
            if changed_file.startswith('dougbot/extensions/') and changed_file.endswith('.py'):
                reload_extensions.append(changed_file)
            elif changed_file.endswith('.py'):
                restart_bot = True
                break

        try:
            if len(reload_extensions) > 0:
                await self._process_commands(cmds)
            if restart_bot:
                await self._restart_bot()
        except subprocess.CalledProcessError:
            if ctx is not None:
                await self.bot.confusion(ctx.message)

        if not restart_bot:
            for ext in reload_extensions:
                try:
                    self.bot.reload_extension(ext.replace('/', '.')[:-3])
                except ExtensionNotLoaded:  # New extension
                    self.bot.load_extension(ext.replace('/', '.')[:-3])
                except ExtensionNotFound:
                    if ctx is not None:
                        await self.bot.confusion(ctx.message, f'{ext} could not be imported.')
                except NoEntryPointError:
                    # Is not a proper extension, so must be extension support.
                    # Could be a newly-added feature, which can be ignored, or a change in how existing support works,
                    # which means that the bot would have to be restarted to get all extensions that use it up to date.
                    await self._restart_bot()
                    break
                except ExtensionFailed:
                    if ctx is not None:
                        await self.bot.confusion(ctx.message, f'{ext} setup function execution error.')

        os.chdir(cwd)

    @staticmethod
    async def _restart_bot():
        p = subprocess.Popen(['reset.bat', str(os.getpid())], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()

    @staticmethod
    async def _process_commands(cmds):
        if cmds is None:
            return
        for command in cmds:
            subprocess.check_call(command)


def setup(bot):
    bot.add_cog(Delivery(bot))
