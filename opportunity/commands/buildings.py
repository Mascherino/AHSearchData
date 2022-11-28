import logging
import string

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
from components.views import Listings

if TYPE_CHECKING:
    from opportunity.opportunity import Bot

class Buildings(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)

    @app_commands.command()
    @app_commands.autocomplete()
    async def buildings(
        self,
        interaction: discord.Interaction
        # category: Literal["Core", "Advanced", "Special", "All"] = "All"
    ) -> None:
        await interaction.response.defer(thinking=True)
        facs = []
        artifacts = []
        try:
            buildings: Optional[List[Dict[str, str]]]
            buildings = self.bot.api.get_buildings()
            if buildings:
                bldg_list: Optional[List[str]] = self.bot.api.extract_data(
                    buildings, "name")
                if bldg_list:
                    for item in bldg_list:
                        if item not in ["total_space", "available_space"]:
                            name = item.rsplit("_", 1)
                            if len(name) > 1:
                                building = string.capwords(
                                    name[0].replace("_", " "))
                                if name[1] == "A":
                                    artifacts.append(building)
                                elif building not in facs:
                                    facs.append(building)
                desc = "List of all buildings"
                em_msg = discord.Embed(title="Buildings", description=desc,
                                       color=Color.GREEN)
                em_msg.add_field(name="Factories", value="\n".join(facs),
                                 inline=True)
                em_msg.add_field(name="Artifacts", value="\n".join(artifacts),
                                 inline=True)
                await interaction.followup.send(embed=em_msg)
        except Exception as e:
            self.logger.error(e)
            await interaction.followup.send(f"Error listing buildings.\n{e}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Buildings(bot))
