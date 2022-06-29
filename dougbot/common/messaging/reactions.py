from nextcord import Message
from nextcord.ext.commands import Context


async def check_log(message, error_text=None, *, delete_text_after=None, delete_message_after=None):
    page_emoji = '\U0001F4C4'
    await reaction_response(message, page_emoji, error_text, delete_text_after=delete_text_after, delete_message_after=delete_message_after)


async def confusion(message, error_text=None, *, delete_text_after=None, delete_message_after=None):
    question_emoji = '\U00002753'
    await reaction_response(message, question_emoji, error_text, delete_text_after=delete_text_after, delete_message_after=delete_message_after)


async def confirmation(message, confirm_text=None, *, delete_text_after=None, delete_message_after=None):
    ok_hand_emoji = '\U0001F44C'
    await reaction_response(message, ok_hand_emoji, confirm_text, delete_text_after=delete_text_after, delete_message_after=delete_message_after)


async def reaction_response(message, emoji, text=None, *, delete_text_after=None, delete_message_after=None):
    await message.add_reaction(emoji)

    if text:
        await message.channel.send(text, delete_after=delete_text_after)

    if delete_message_after:
        await message.delete(delay=delete_message_after)


async def users_who_reacted(context: Context, message: Message):
    # Have to re-fetch message to get updated reactions list
    message = await context.fetch_message(message.id)

    users = []
    for reaction in message.reactions:
        async for user in reaction.users():
            if user not in users and not user.bot:
                users.append(user)

    return users
