import logging
import importlib.util

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Any
)

import discord
from discord import app_commands
from discord.ext import commands

from utils import Color

if TYPE_CHECKING:
    from opportunity.opportunity import Bot



class Help(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)
        self.commands = [extension for extension
                         in self.bot.extensions if "command" in extension]

    async def command_ac(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        choices = self.commands
        return [
            app_commands.Choice(name=command.split(".")[1], value=command)
            for command in choices if current.lower() in command.lower()
        ]

    @app_commands.command()
    @app_commands.autocomplete(command=command_ac)
    async def help(
            self,
            interaction: discord.Interaction,
            command: str
    ) -> None:
        await interaction.response.defer(thinking=True)

        self.logger.info(f"Displaying help for {command}")
        spec = importlib.util.find_spec(command)
        if spec is None:
            print("no spec found")
            return
        lib = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(lib)  # type: ignore
        except Exception as e:
            raise Exception
        try:
            func = getattr(lib, "help")
        except AttributeError:
            em_msg = discord.Embed(
                title="Error",
                description=f"No help available for " +
                            f"command '{command.split('.')[1]}'",
                color=Color.RED
            )
            await interaction.followup.send(embed=em_msg)
            return
        help_str = await func()
        em_msg = discord.Embed(
            title=f"Help for {command.split('.')[1]}",
            description=help_str,
            color=Color.GREEN
        )
        await interaction.followup.send(embed=em_msg)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot))
