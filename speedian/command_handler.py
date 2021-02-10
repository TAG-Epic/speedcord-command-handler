"""
Created by Epic at 12/31/20
"""
from .types import Cog, CommandContext

from importlib import import_module
from logging import getLogger
from speedcord.http import Route


class CommandHandler:
    def __init__(self, client, client_id, *, prefix=None, cogs_directory="cogs", guild_id=None, disable_mentions=True):
        self.client = client
        self.client_id = client_id
        self.logger = getLogger("speedian.command_handler")
        self.loop = client.loop
        self.prefix = prefix
        self.allow_text_commands = self.prefix is not None
        self.cogs_directory = cogs_directory
        self.cogs = []
        self.commands = []
        self.guild_id = guild_id
        self.to_be_added = []
        self.disable_mentions = disable_mentions
        self.client.event_dispatcher.register("INTERACTION_CREATE", self.interaction_create)

    def load_extension(self, extension_name):
        self.loop.create_task(self._load_extension(extension_name))

    async def _load_extension(self, extension_name):
        extension = import_module("." + extension_name, self.cogs_directory)
        for cog_attr_name in dir(extension):
            cog_attr = getattr(extension, cog_attr_name)
            if Cog in getattr(cog_attr, "__bases__", []):
                self.logger.debug("Adding cog \"%s\"" % cog_attr.__name__)
                await self.add_cog(cog_attr)

    async def add_cog(self, cog_uninitialized):
        cog = cog_uninitialized(self.client)
        self.cogs.append(cog)
        for command in cog.commands:
            self.commands.append(command)
            self.create_command(command)
        await self.push_commands()

    def create_command(self, command):
        data = command.export_slash_command()
        self.logger.debug("Adding slash command with data %s" % data)
        self.to_be_added.append(data)

    async def push_commands(self):
        await self.client.connected.wait()
        if self.guild_id is None:
            r = Route("PUT", "/applications/{application_id}/commands", application_id=self.client_id)
        else:
            r = Route("PUT", "/applications/{application_id}/guilds/{guild_id}/commands", application_id=self.client_id,
                      guild_id=self.guild_id)
        self.logger.debug("Pushing commands")
        await self.client.http.request(r, json=self.to_be_added)

    def get_command(self, command_name):
        for command in self.commands:
            if command.name == command_name:
                return command

    async def interaction_create(self, data, shard):
        if data is None:
            self.logger.warning("Discord sent us incomplete data!")
            return

        self.logger.debug("Received interaction data %s" % data)
        token = data["token"]
        interaction_id = data["id"]
        args = data["data"].get("options") or []
        parsed_args = {opt["name"]: opt["value"] for opt in args}
        command = self.get_command(data["data"]["name"])

        if command is None:
            self.logger.warning("Slash command not found!")
            return

        if not command.silent:
            r = Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback",
                      interaction_id=interaction_id, interaction_token=token)
            await self.client.http.request(r, json={"type": 5})

        new_args = {}

        for name, value in parsed_args.items():
            option = command.get_option(name)
            if option.choices is not None:
                new_args[name] = option.choices[value]["name"]
                continue
            new_args[name] = value

        self.logger.debug("Command %s was ran" % command.name)
        context = CommandContext(command=command, token=token, params=parsed_args, client=self.client, data=data,
                                 disable_mentions=self.disable_mentions)
        try:
            await command.func(command.cog, context, **new_args)
        except Exception as e:
            self.logger.error("An error occurred while running %s" % command.name, exc_info=e)
            await context.send("Uh oh, an error occurred while running your command.")
