import os
import subprocess
import sys

from discord.ext import commands
from discord.ext.commands.errors import *

from dougbot.extensions.util.admin_check import admin_command


class Delivery(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin_command()
    async def restart(self, ctx):
        await self._restart_bot(ctx)

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
    async def update_pkgs(self, ctx):
        await self._update(ctx, ['python', os.path.join(self.bot.ROOT_DIR, 'setup.py')])
        await self._restart_bot(ctx)

    async def _update(self, ctx, *cmds):
        if ctx is None or cmds is None:
            return

        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)

        # Find which files will change - core files or extensions.
        # Extensions can be reloaded, core files require restarting
        await self._process_commands(['git', 'fetch'])
        changed_files = subprocess.check_output(['git', 'diff', 'master', 'origin/master', '--name-only'])
        if len(changed_files) == 0:
            return
        changed_files = str(changed_files, 'utf-8').splitlines()

        reload_extensions = []
        restart_bot = False
        for changed_file in changed_files:
            changed_file = changed_file.strip()
            # Delivery code cannot update itself without issues.
            if changed_file.startswith('dougbot/extensions/delivery'):
                restart_bot = True
                break
            elif changed_file.startswith('dougbot/extensions/') and changed_file.endswith('.py'):
                reload_extensions.append(changed_file)
            # Must be a core/common file, which would require restarting
            elif changed_file.startswith('dougbot/') and changed_file.endswith('.py'):
                restart_bot = True
                print('RESTART IS TRUE')
                break

        # Update code
        try:
            if len(reload_extensions) > 0:
                await self._process_commands(*cmds)
        except subprocess.CalledProcessError:
            if ctx is not None:
                await self.bot.confusion(ctx.message)
                os.chdir(cwd)
                return

        if restart_bot:
            await self._restart_bot(ctx)
            os.chdir(cwd)
            return

        for extension in reload_extensions:
            try:
                self.bot.reload_extension(extension.replace('/', '.')[:-len('.py')])
            except ExtensionNotLoaded:  # New extension
                self.bot.load_extension(extension.replace('/', '.')[:-len('.py')])
            except ExtensionNotFound:
                if ctx is not None:
                    await self.bot.confusion(ctx.message, f'{extension} could not be imported.')
            except NoEntryPointError:
                # Is not a proper extension, so must be extension support.
                # Could be a newly-added feature, which can be ignored, or a change in how existing support works,
                # which means that the bot would have to be restarted to get all extensions that use it up to date.
                await self._restart_bot(ctx)
                break
            except ExtensionFailed:
                if ctx is not None:
                    await self.bot.confusion(ctx.message, f'{extension} setup function execution error.')

        os.chdir(cwd)

    async def _restart_bot(self, ctx):
        await ctx.send('Restarting...')
        try:
            os.execv(os.path.join(self.bot.ROOT_DIR, 'run.bat'), sys.argv)
        except Exception as e:
            print(e)
        await ctx.send('Failed to restart')

    @staticmethod
    async def _process_commands(*cmds):
        if cmds is None:
            return
        for command in cmds:
            print(command)
            retcode = subprocess.call(command)
            print(retcode)


def setup(bot):
    bot.add_cog(Delivery(bot))
