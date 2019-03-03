import enum
import os
import subprocess
import sys
import threading

from discord.ext import commands


class DeliverySystem:

    class TimeFrame(enum.Enum):
        DAILY = 1,
        WEEKLY = 2,
        MONTHLY = 3
        INVALID = 4

        string_to_frame = {'daily': DAILY, 'weekly': WEEKLY, 'monthly': MONTHLY, None: INVALID}

        @classmethod
        def as_time_frame(cls, frame):
            if frame is None or frame not in cls.string_to_frame.keys():
                return cls.INVALID
            return cls.string_to_frame[frame]

    def __init__(self, bot, time_frame=TimeFrame.DAILY):
        # TODO PULL TIME FRAME FROM KVSTORE???
        self.bot = bot
        self._time_frame = time_frame
        self._schedule_thread = None
        self._start_schedule(self._time_frame)

    @commands.command(pass_context=True)
    async def schedule_updates(self, ctx, when: str):
        if ctx is None or when is None:
            return
        time_frame = self.TimeFrame.as_time_frame(when)
        self._time_frame = time_frame
        await self.end_schedule()  # TODO CAN WE CALL ANOTHER COMMAND LIKE THIS???
        self._start_schedule(time_frame)

    @commands.command()
    async def end_schedule(self):
        if self._schedule_thread is not None:
            self._schedule_thread.cancel()
            self._schedule_thread = None

    def _start_schedule(self, when):
        if when == self.TimeFrame.MONTHLY:
            delay = 31 * 24 * 60 * 60
        elif when == self.TimeFrame.WEEKLY:
            delay = 7 * 24 * 60 * 60
        else:  # Daily or Invalid; if Invalid, do daily.
            delay = 24 * 60 * 60

        self._schedule_thread = threading.Timer(delay, self._soft_update)
        self._schedule_thread.start()

    # TODO CONSOLIDATE CODE

    @commands.command(pass_context=True)
    async def update(self, ctx):
        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)
        try:
            subprocess.check_call(['git', 'pull'])

            pid = os.getpid()

            # Restart ourself
            p = subprocess.Popen(['reset.bat', str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
        except subprocess.CalledProcessError:
            if ctx is not None:
                await self.bot.confusion(ctx.message)
        finally:
            os.chdir(cwd)

    def _soft_update(self):
        # TODO ISSUE IS WE LOSE THE SCHEDULE IF DONE, SO NEED A KVSTORE
        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)
        try:
            subprocess.check_call(['git', 'pull'])

            pid = os.getpid()

            # Restart ourself
            p = subprocess.Popen(['reset.bat', str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
        except subprocess.CalledProcessError:
            print('Scheduled soft update failed.', file=sys.stderr)
        finally:
            os.chdir(cwd)

    @commands.command(pass_context=True)
    async def force_update(self, ctx):
        if ctx is None:
            return

        cwd = os.getcwd()
        os.chdir(self.bot.ROOT_DIR)
        try:
            subprocess.check_call(['git', 'fetch', '--all'])
            subprocess.check_call(['git', 'reset', '--hard', 'origin/master'])

            pid = os.getpid()

            # Restart ourself
            p = subprocess.Popen(['reset.bat', str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
        except subprocess.CalledProcessError:
            await self.bot.confusion(ctx.message)
        finally:
            os.chdir(cwd)


def setup(bot):
    bot.add_cog(DeliverySystem(bot))
