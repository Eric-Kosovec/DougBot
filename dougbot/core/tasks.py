from nextcord.ext import tasks

from dougbot.common import database


@tasks.loop(hours=24 * 5)
async def touch_supabase_api():
    """
    Supabase pauses projects after 1 week of inactivity, so touch an API endpoint that should have no data
    """
    await database.check_connection()
