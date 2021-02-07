"""
Created by Epic at 12/31/20
"""
from .types import Command, Option


def addmod(mod, mod_type):
    def inner(func):
        mods = getattr(func, mod_type, [])
        mods.append(mod)
        setattr(func, mod_type, mods)
        return func

    return inner


def command(*args, **kwargs):
    def inner(func):
        return Command(func, *args, **kwargs)

    return inner


def option(name, option_type, *, description="\u200B", choices=None, required=True, default=False):
    return addmod(
        Option(name, option_type, description=description, choices=choices, required=required, default=default),
        "options")
