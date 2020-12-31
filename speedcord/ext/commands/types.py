"""
Created by Epic at 12/31/20
"""
from logging import getLogger


class Cog:
    def __init__(self, client):
        self.client = client
        self.logger = getLogger("speedcord.ext.commmand-handler.cogs.%s" % self.__module__)
        self.commands = []
        self.event_listeners = []
