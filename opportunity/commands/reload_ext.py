import logging

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Optional,
    Dict,
    List,
    Literal
)

import discord
from discord import app_commands
from discord.ext import commands

from utils import Color

if TYPE_CHECKING:
    from opportunity.opportunity import Bot

async def check_isme(interaction: discord.Interaction) -> bool:
    return interaction.user.id == 227087936464748545

class Reload_ext(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)

    async def extension_ac(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        choices: List[str] = list(self.bot.extensions.keys())
        return [
            app_commands.Choice(name=building, value=building)
            for building in choices if current.lower() in building.lower()
        ]

    @app_commands.command()
    @app_commands.autocomplete(extension=extension_ac)
    @app_commands.check(check_isme)
    async def reload_ext(
        self,
        interaction: discord.Interaction,
        extension: str
    ) -> None:
        try:
            await self.bot.reload_extension(extension)
            self.logger.info(f"Successfully reloaded '{extension}'")
            em_msg = discord.Embed(
                title="Reload Extension",
                description=f"Successfully reloaded '{extension}'",
                color=Color.GREEN)
            await interaction.response.send_message(embed=em_msg)
        except Exception as e:
            self.logger.error(e)

    @reload_ext.error
    async def reload_ext_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.errors.AppCommandError
    ) -> None:
        em_msg = discord.Embed(
            title="Error",
            color=Color.RED)
        if isinstance(error, app_commands.errors.CheckFailure):
            em_msg.description = "Error: Command can only be " + \
                                 "invoked by <@227087936464748545>"
            await interaction.response.send_message(embed=em_msg)
        else:
            em_msg.description = str(error)
            await interaction.response.send_message(embed=em_msg)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Reload_ext(bot))
