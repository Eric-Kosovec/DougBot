from nextcord.ext import tasks

from dougbot.common import database
from dougbot.common.logevent import LogEvent


@tasks.loop(hours=24 * 4)
async def touch_supabase_api():
    """
    Supabase pauses projects after 1 week of inactivity
    """
    await database.check_connection()

    LogEvent(__file__) \
        .message('Touched Supabase API') \
        .info()


async def start_tasks():
    touch_supabase_api.start()
