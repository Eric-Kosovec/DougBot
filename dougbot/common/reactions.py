
async def check_log(message, error_msg=None):
    page_emoji = '\U0001F4C4'
    await reaction_and_response(message, page_emoji, error_msg)


async def confusion(message, error_msg=None):
    question_emoji = '\U00002753'
    await reaction_and_response(message, question_emoji, error_msg)


async def confirmation(message, confirm_msg=None):
    ok_hand_emoji = '\U0001F44C'
    await reaction_and_response(message, ok_hand_emoji, confirm_msg)


async def reaction_and_response(message, emoji, text=None):
    await message.add_reaction(emoji)
    if text is not None:
        await message.channel.send(text)
