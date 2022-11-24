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
from components.views import Listings

if TYPE_CHECKING:
    from opportunity.opportunity import Bot

async def core_ac(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    print("core_ac")
    core: Optional[str] = interaction.namespace.core
    choices = [
        'Solar Panel', 'Water Filter', 'C.A.D.', 'Greenhouse',
        'Sab Reactor', 'Smelter', 'Chem Lab', 'Machine Shop',
        '3D Print Shop'
    ]
    if interaction.namespace.rarity == "Special":
        choices = []
    elif core:
        choices = [s for s in choices if core.lower() in s.lower()]
    else:
        choices = []
    return [
        app_commands.Choice(name=building, value=building)
        for building in choices if current.lower() in building.lower()
    ]

async def advanced_ac(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    ns: app_commands.Namespace = interaction.namespace
    choices = []
    if ns.rarity == "Special":
        pass
    else:
        if ns.level == 1:
            choices.append("Metis Shield")
        if ns.level <= 5:
            choices.extend(["Habitat", "Shelter"])
        if (ns.rarity == "Common" and ns.level <= 10) or \
                (ns.rarity == "Uncommon" and ns.level <= 8) or \
                (ns.rarity == "Rare" and ns.level <= 6) or \
                (ns.rarity in ["Epic", "Legendary", "Mythic"] and
                 ns.level <= 5):
            choices.extend(['Rover Works', 'Engineering Bay',
                            'Thorium Reactor', 'Composter'])
        choices.extend(["Mining Rig", "Polar Workshop", "GrindnBrew"])
    return [
        app_commands.Choice(name=building, value=building)
        for building in choices if current.lower() in building.lower()
    ]

async def special_ac(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    ns: app_commands.Namespace = interaction.namespace
    choices = []
    if not ns.rarity == "Special":
        pass
    else:
        if ns.level <= 5:
            choices.extend(["Bazaar", "Teashop"])
        if ns.level <= 6:
            choices.append("Cantina")
    choices.extend(['Pirate Radio', 'Library', 'Training Hall', 'Gallery'])
    return [
        app_commands.Choice(name=building, value=building)
        for building in choices if current.lower() in building.lower()
    ]

async def artifact_ac(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    choices = []  # TODO artifact list
    return [
        app_commands.Choice(name=building, value=building)
        for building in choices if current.lower() in building.lower()
    ]

class Search(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)

    @app_commands.command()
    @app_commands.autocomplete(core=core_ac, advanced=advanced_ac,
                               special=special_ac)
    async def search(
            self,
            interaction: discord.Interaction,
            generation: Literal["Gen 1", "Gen 2", "Gen 3"],
            level: app_commands.Range[int, 1, 10],
            rarity: Literal["Common", "Uncommon", "Rare", "Epic",
                            "Legendary", "Mythic", "Special"],
            core: str = "",
            advanced: str = "",
            special: str = "",
            amount: int = 1
    ) -> None:
        await interaction.response.defer(thinking=True)
        args: Dict[str, str] = {k: v for k, v in locals().copy().items()
                                if v and k in
                                ["core", "advanced", "special", "artifact"]}
        if len(args) > 1:
            await interaction.followup.send(embed=discord.Embed(
                title="Error",
                description="You cannot choose more than one building",
                color=Color.RED))
            return
        if (rarity == "Special") and not special:
            await interaction.followup.send(embed=discord.Embed(
                title="Error",
                description="You must select a special " +
                            "building when using special rarity",
                color=Color.RED))
            return

        building: str = list(args.items())[0][1].lower().replace(".", "")
        if building in ["thorium reactor", "ground control"]:
            building = building.replace(" ", "-")
        else:
            building = building.replace(" ", "_")
        if generation == "Gen 2":
            if building in [
                "solar_panel", "cad", "water_filter",
                "greenhouse", "polar_workshop"
            ]:
                building = building + "-22"
            else:
                building = building + "-gen2"
        elif generation == "Gen 3":
            building = building + "-gen3"
        building = building + "_" + rarity[0] + str(level)
        self.logger.info(f"Getting listings for {building}")
        listings = self.bot.api.get_listings(building, 1, amount)
        if listings:
            description = f"Listings containing {amount} {building} (page 1)"
            em_msg = discord.Embed(
                title="Listings",
                description=description,
                color=Color.GREEN)

            em_msg.add_field(
                name="Listings",
                value="\n".join([
                    listings[item]["link"] for item in listings.keys()]),
                inline=True)

            em_msg.add_field(
                name="Cost",
                value="\n".join([
                    str(listings[item]["price"]) +
                    " " + listings[item]["token_symbol"]
                    for item in listings.keys()]),
                inline=True)

            em_msg.add_field(
                name="Land(s)",
                value="\n".join([
                    listings[item]["land"]["rarity"]
                    if isinstance(listings[item]["land"], dict)
                    else "Bundle" for item in listings.keys()]),
                inline=True)
            view = Listings(building, 1)
            await interaction.followup.send(embed=em_msg, view=view)
        else:
            await interaction.followup.send(embed=discord.Embed(
                title="Error",
                description="Could not find any listings " +
                            "matching the given parameters",
                color=Color.RED))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Search(bot))
