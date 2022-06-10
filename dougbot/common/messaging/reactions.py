async def check_log(message, error_text=None, *, delete_after=None):
    page_emoji = '\U0001F4C4'
    await reaction_and_response(message, page_emoji, error_text, delete_after=delete_after)


async def confusion(message, error_text=None, *, delete_after=None):
    question_emoji = '\U00002753'
    await reaction_and_response(message, question_emoji, error_text, delete_after=delete_after)


async def confirmation(message, confirm_text=None, *, delete_after=None):
    ok_hand_emoji = '\U0001F44C'
    await reaction_and_response(message, ok_hand_emoji, confirm_text, delete_after=delete_after)


async def reaction_and_response(message, emoji, text=None, *, delete_after=None):
    await message.add_reaction(emoji)
    if text:
        await message.channel.send(text, delete_after=delete_after)
