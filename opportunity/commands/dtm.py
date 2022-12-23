import logging

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Dict,
    Any
)

import discord
from discord import app_commands
from discord.ext import commands

from utils import Color, get_dtm_listings

if TYPE_CHECKING:
    from opportunity.opportunity import Bot

class DTM(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)
        self.url = f"https://wax.api.atomicassets.io/atomicmarket/v2/" + \
                   f"sales?state=1&collection_name=onmars" + \
                   f"&schema_name=land.plots&immutable_data.quadrangle=" + \
                   f"Coprates&page=1&limit=100&order=asc&sort=price"

    @app_commands.command(description="List all plots available for" +
                                      "sale on MC-18 'Possible sulfates in " +
                                      "Coprates Chasma'")
    async def dtm(
            self,
            interaction: discord.Interaction,
    ) -> None:
        await interaction.response.defer(thinking=True)
        if not (listings := self.bot.api.get_custom_listings(self.url)):
            return
        listings = get_dtm_listings(listings)
        if not listings:
            await interaction.followup.send(embed=discord.Embed(
                title="Plots for sale",
                description="No plots for sale",
                color=Color.GREEN))
            return
        em_msg = discord.Embed(
            title="Plots for sale on settlement DTM",
            color=Color.GREEN)
        self._build_embed(interaction, em_msg, listings)

        await interaction.followup.send(embed=em_msg)

    def _build_embed(
        self,
        interaction: discord.Interaction,
        em_msg: discord.Embed,
        listings: Dict[int, Any]
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
                        f"{str(listings[item]['price'])} " +
                        f"{listings[item]['token_symbol']}",
                        listings[item]["land"]["data"]["rarity"]
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
                    listings[item]["land"]["data"]["rarity"]
                    if isinstance(listings[item]["land"], dict)
                    else "Bundle" for item in listings.keys()]),
                inline=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DTM(bot))
