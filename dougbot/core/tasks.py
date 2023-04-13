from nextcord.ext import tasks

from dougbot.common import database


@tasks.loop(hours=24 * 2)
async def touch_supabase_api():
    """
    Supabase emails after ~4 days of inactivity and pauses after 5
    """
    await database.check_connection()


async def start_tasks():
    if not touch_supabase_api.is_running():
        touch_supabase_api.start()
