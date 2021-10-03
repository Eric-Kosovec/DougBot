from discord.ext import commands

import inspect
import functools


def argument_parse(func):

    # Get func types
    print(func.__code__.co_varnames)
    print(inspect.signature(func))
    print(type(inspect.signature(func).parameters))

    @functools.wraps(func)
    async def predicate(*args, **kwargs):
        print(f'args {args}; kwargs: {kwargs}')

    return predicate
