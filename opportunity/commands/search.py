import logging

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Optional,
    Dict,
    List,
    Literal,
    Union,
    Any
)

import discord
from discord import app_commands
from discord.ext import commands

from utils import Color
from components.views import Listings, AllLevelListings

if TYPE_CHECKING:
    from opportunity.opportunity import Bot

async def core_ac(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    choices = [
        'Solar Panel', 'Water Filter', 'C.A.D.', 'Greenhouse',
        'Sab Reactor', 'Smelter', 'Chem Lab', 'Machine Shop',
        '3D Print Shop'
    ]
    if interaction.namespace.rarity == "Special":
        choices = []
    choices = sorted(choices)
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
        choices.append("Metis Shield")
        choices.extend(["Concrete Habitat", "Shelter"])
        choices.extend(['Rover Works', 'Engineering Bay',
                        'Thorium Reactor', 'Composter'])
        choices.extend(["Mining Rig", "Polar Workshop", "GrindnBrew"])
        choices = sorted(choices)
    return [
        app_commands.Choice(name=building, value=building)
        for building in choices if current.lower() in building.lower()
    ]

async def special_ac(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    ns: app_commands.Namespace = interaction.namespace
    choices: List[str] = []
    if ns.rarity == "Special":
        choices.extend(["Bazaar", "Teashop"])
        choices.append("Cantina")
        choices.extend(['Pirate Radio', 'Library',
                        'Training Hall', 'Gallery'])
    return [
        app_commands.Choice(name=building, value=building)
        for building in choices if current.lower() in building.lower()
    ]

class Search(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)
        if buildings := self.bot.api.get_buildings():
            self.buildings = {item["name"]: item["name"] for item in buildings}
        self.maxLevel = self.bot.data["maxLevel"]

    @app_commands.command(description="Search for buildings" +
                                      " on plots on AtomicHub")
    @app_commands.autocomplete(core=core_ac, advanced=advanced_ac,
                               special=special_ac)
    async def search(
            self,
            interaction: discord.Interaction,
            generation: Literal["Gen 1", "Gen 2", "Gen 3"],
            level: Literal["1", "2", "3", "4", "5", "6", "7",
                           "8", "9", "10", "*"],
            rarity: Literal["Common", "Uncommon", "Rare", "Epic",
                            "Legendary", "Mythic", "Special"],
            core: str = "",
            advanced: str = "",
            special: str = "",
            amount: int = 1
    ) -> None:
        if level == "*" and rarity in ["Common", "Uncommon", "Rare"]:
            em_msg = discord.Embed(
                title="Error",
                description="You cannot retrieve all " +
                            "levels for rarities **Rare** or **lower**",
                color=Color.RED)
            await interaction.response.send_message(embed=em_msg)
            return
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
        try:
            building: str = list(args.items())[0][1].lower().replace(".", "")
        except IndexError as e:
            self.logger.error(e)
            em_msg = discord.Embed(
                title="Error",
                description="You must specify exactly one category " +
                            "(core, advanced or special)",
                color=Color.RED)
            await interaction.followup.send(embed=em_msg)
            return
        if building in ["thorium reactor", "ground control"]:
            building = building.replace(" ", "-")
        else:
            building = building.replace(" ", "_")
        if generation == "Gen 2":
            if temp := self.buildings.get(building + "-22", None) or \
                    self.buildings.get(building + "-gen2", None):
                building = temp
        elif generation == "Gen 3":
            if temp := self.buildings.get(building + "-gen3", None):
                building = temp
        building = building + "_" + rarity[0] + str(level)
        self.logger.info(f"Getting listings for {building}")
        building_name: str = building.rsplit("_", 1)[0]
        if level == "*":
            level = "1"
            building = building.replace("*", level)
            listings = self.bot.api.get_listings(building, 1, amount)
            lvl: int = int(level)
            while not listings:
                if lvl < int(self.maxLevel[building_name][rarity[0]]):
                    building.replace(level, str(lvl+1))
                    lvl += 1
                    listings = self.bot.api.get_listings(building, 1, amount)
                else:
                    em_msg = discord.Embed(title="Listings", color=0xff0000)
                    em_msg.add_field(
                        name="Listings",
                        value=f"No listings found. (level {str(lvl)})",
                        inline=False)
                    await interaction.followup.send(embed=em_msg)
                    return
            view = AllLevelListings(self.bot, building, lvl, 1)

        else:
            listings = self.bot.api.get_listings(building, 1, amount)
            view = Listings(building, 1)
            if not listings:
                await interaction.followup.send(embed=discord.Embed(
                    title="Error",
                    description="Could not find any listings " +
                                "matching the given parameters",
                    color=Color.RED))
                return
        description = f"Listings containing **{amount}** " + \
                      f"**{rarity} {list(args.items())[0][1]} " + \
                      f"Level {level}** (page 1)"
        em_msg = discord.Embed(
            title="Listings",
            description=description,
            color=Color.GREEN)
        self._build_embed(interaction, em_msg, listings)
        await interaction.followup.send(embed=em_msg, view=view)


    def _build_embed(
        self,
        interaction: discord.Interaction,
        em_msg: discord.Embed,
        listings: Dict[Union[str, int], Any]
    ) -> None:
        mobile: bool = False
        if interaction.guild:
            user = interaction.guild.get_member(interaction.user.id)
            if isinstance(user, discord.Member):
                mobile = user.is_on_mobile()
        if mobile:
            for item in listings:
                em_msg.add_field(
                    name=f"{listings[item]['name']}",
                    value="\n".join([
                        f"[Link]({listings[item]['link']})",
                        f"{listings[item]['price']} " +
                        f"{listings[item]['token_symbol']}",
                        listings[item]["land"]["rarity"]
                        if isinstance(listings[item]["land"], dict)
                        else "Bundle"])
                )
        else:
            em_msg.add_field(
                name="Listings",
                value="\n".join([
                    f"[Link]({listings[item]['link']})"
                    for item in listings.keys()]),
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

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Search(bot))
