"""
Created by Epic at 12/31/20
"""
from logging import getLogger


class Cog:
    def __init__(self, client):
        self.client = client
        self.logger = getLogger("speedian.cogs.%s" % self.__module__)
        self.commands = []
        self.event_listeners = []

        for attribute_name in dir(self):
            attr = getattr(self, attribute_name)
            if isinstance(attr, Command):
                self.commands.append(attr)


class Command:
    def __init__(self, func, name=None, *, description="\u200B", silent=False):
        self.func = func
        self.name = name or func.__name__
        self.description = description

        self.data = {}
        self.options = getattr(func, "options", [])
        self.silent = silent

    def export_slash_command(self):
        return {
            "name": self.name,
            "description": self.description,
            "options": [i.export() for i in self.options]
        }


class Option:
    def __init__(self, name, option_type, *, description, choices, default, required):
        if choices is not None:
            self.choices = [{"name": choice, "value": index} for index, choice in enumerate(choices)]
        else:
            self.choices = None
        self.name = name
        self.description = description
        self.required = required
        self.default = default

        if required and default:
            raise TypeError("Default has to be optional.")
        if option_type not in OPTION_TYPES:
            raise TypeError("Invalid option type")
        self.type = OPTION_TYPES[option_type]

    def export(self):
        data = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required": self.required,
            "default": self.default
        }
        if self.choices:
            data["choices"] = self.choices
        return data


# Option types
class UserType:
    pass


class ChannelType:
    pass


class RoleType:
    pass


OPTION_TYPES = {
    str: 3,
    int: 4,
    bool: 5,
    UserType: 6,
    ChannelType: 7,
    RoleType: 8
}
