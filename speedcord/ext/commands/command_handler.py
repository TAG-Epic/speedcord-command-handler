"""
Created by Epic at 12/31/20
"""
from .types import Cog

from importlib import import_module
from logging import getLogger


class CommandHandler:
    def __init__(self, client, *, prefix=None, cogs_directory="cogs"):
        self.client = client
        self.logger = getLogger("speedcord.ext.commands.command_handler")
        self.loop = client.loop
        self.prefix = prefix
        self.allow_text_commands = self.prefix is not None
        self.cogs_directory = cogs_directory
        self.cogs = []
        self.commands = []
        self.inject()

    def load_extension(self, extension_name):
        self.loop.create_task(self._load_extension(extension_name))

    async def _load_extension(self, extension_name):
        extension = import_module("." + extension_name, self.cogs_directory)
        for cog_attr_name in dir(extension):
            cog_attr = getattr(extension, cog_attr_name)
            if Cog in getattr(cog_attr, "__bases__", []):
                self.logger.debug("Adding cog")
                await self.add_cog(cog_attr)

    async def add_cog(self, cog_uninitialized):
        cog = cog_uninitialized(self.client)
        self.cogs.append(cog)
        for command in cog.commands:
            self.commands.append(command)
            await self.create_command(command)

    async def create_command(self, command):
        pass

    def inject(self):
        pass
