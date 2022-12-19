import logging
import string

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Optional,
    Dict,
    List,
    Literal,
    Any
)

import discord
from discord import app_commands
from discord.ext import commands

from utils import Color

if TYPE_CHECKING:
    from opportunity.opportunity import Bot

class Upgrade(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)
        self.upgrades = self.bot.data["buildingUpgrades"]
        if temp := self.bot.api.get_building_names_clean():
            self.temp = temp
        self.buildings_clean = [string.capwords(x.replace("_", " "), " ")
                                for x in self.temp]
        if buildings := self.bot.api.get_buildings():
            self.buildings = {item["name"]: item["name"] for item in buildings}

    async def building_ac(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        building: Optional[str] = interaction.namespace.building
        choices = self.buildings_clean
        if building and choices:
            choices = [s for s in choices if building.lower() in s.lower()]
        else:
            choices = []
        return [
            app_commands.Choice(name=building, value=building)
            for building in choices if current.lower() in building.lower()
        ]

    @app_commands.command()
    @app_commands.autocomplete(building=building_ac)
    async def upgrade(
            self,
            interaction: discord.Interaction,
            building: str,
            rarity: Literal["Common", "Uncommon", "Rare", "Epic",
                            "Legendary", "Mythic", "Special"],
            start: app_commands.Range[int, 1, 9],
            end: app_commands.Range[int, 2, 10],
            include_building: bool = False,
            generation: str = "Gen 2"
    ) -> None:
        await interaction.response.defer(thinking=True)
        if end <= start:
            await interaction.followup.send(embed=discord.Embed(
                title="Error",
                description="End level must be higher than the start level",
                color=Color.RED))
            return

        if temp := self.bot.api.get_market_stats():
            market_data: List[Dict[str, Any]] = temp["data"]["data"]
        else:
            await interaction.followup.send(embed=discord.Embed(
                title="Error",
                description="Cannot get market stats, try again later",
                color=Color.RED
            ))
            return

        self.logger.info(f"Iterating over levels {start} " +
                         f"to {end} for {building}")
        building_prep = building.replace(" ", "_").lower()
        if building_prep in ["thorium reactor", "ground control"]:
            building_prep = building_prep.replace(" ", "-")
        else:
            building_prep = building_prep.replace(" ", "_")
        if generation == "Gen 2":
            if temp := self.buildings.get(building_prep + "-22", None) or \
                    self.buildings.get(building_prep + "-gen2", None):
                building_prep = temp
        elif generation == "Gen 3":
            if temp := self.buildings.get(building_prep + "-gen3", None):
                building_prep = temp
        building_lv = building_prep + "_" + rarity[0]

        found = False
        bprice = "N/A"
        sprice = "N/A"
        for market_item in market_data:
            if market_item["id"] == building_lv + "1":
                bprice = market_item["attributes"]["lastSoldPrice"]
                if found:
                    break
                found = True
            if market_item["id"] == "shard_" + building_lv:
                sprice = market_item["attributes"]["lastSoldPrice"]
                if found:
                    break
                found = True
        currlvl = start+1  # if start != 0 else 2
        result: Dict[str, Any] = {}
        while currlvl <= int(end):
            try:
                current = self.upgrades[building_lv + str(currlvl)]
            except KeyError:
                em_msg = discord.Embed(
                    title="Error",
                    description=f"You cannot upgrade a **{rarity}** " +
                                f"**{building}** to **{currlvl}**, max " +
                                f"level is **{currlvl-1}**", color=Color.RED)
                await interaction.followup.send(embed=em_msg)
                return
            for item in current:
                if item in ["shardsRequired", "upgradePrice"]:
                    if item not in result:
                        result[item] = current[item]
                    else:
                        result[item] += current[item]
            currlvl += 1
        description = f"Requirements to upgrade **{generation} {rarity}** " + \
                      f"**{building}** from **{start}** to **{end}**\n" + \
                      f"Current prices: Building {bprice} Dusk,  " + \
                      f"Shard {sprice} Dusk"
        em_msg = discord.Embed(
            title=f"Upgrade (include building price: {include_building})",
            description=description,
            color=Color.GREEN)
        for item in result:
            em_msg.add_field(
                name="Dusk" if item == "upgradePrice" else "Shards",
                value=str(result[item]))
        total = sum([result.get("upgradePrice", 0),
                     result.get("shardsRequired", 0)*sprice])
        if not (bprice == "N/A") and include_building:
            total += bprice
        em_msg.add_field(
            name="Total Dusk",
            value=str(round(total, 2))
        )
        total_wax = total*self.bot.api.get_wax_dusk()
        em_msg.add_field(
            name="Total WAX",
            value=str(round(total_wax, 2))
        )
        em_msg.add_field(
            name="Total USD",
            value=str(round(total_wax*self.bot.api.get_wax_usd(), 2))
        )
        await interaction.followup.send(embed=em_msg)

async def help() -> str:
    help_msg = """```
The upgrade command is used to calculate
the amount of resources required to level
up a building to a certain level

Input:
-------
building - the building you want to
           calculate the resources for
rarity - the building rarity
start - the level you start at [1-9]
end - the level you want to end at [2-10]

Output:
-------
Returns a list of resources needed to
level up a building from start to end```
"""
    return help_msg

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Upgrade(bot))
