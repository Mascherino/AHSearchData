import discord

from components.api import API
import configparser

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Dict,
    Union,
    Any
)

if TYPE_CHECKING:
    from opportunity.opportunity import Bot

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction,
                      button: discord.ui.Button) -> None:
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction,
                     button: discord.ui.Button) -> None:
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()

class Listings(discord.ui.View):
    def __init__(self, building: str, page: int = 1):
        super().__init__()
        self.page = page
        self.building = building

    @discord.ui.button(label="More results", style=discord.ButtonStyle.green)
    async def more(self, interaction: discord.Interaction,
                   button: discord.ui.Button) -> None:
        config = configparser.ConfigParser()
        config.read("config.cfg")
        api = API(url=config["yourls"]["url"],
                  secret=config["yourls"]["secret"])
        await interaction.response.defer(thinking=True)
        self.page += 1
        listings = api.get_listings(self.building, self.page)
        if listings:
            em_msg = discord.Embed(
                title="Listings",
                description=f"Listings containing {self.building} " +
                            f"(page {self.page})",
                color=0x00ff00)

            _build_listings_embed(interaction, em_msg, listings)
            listing_view = Listings(self.building, self.page)
            await interaction.followup.send(embed=em_msg,
                                            view=listing_view)
        else:
            em_msg = discord.Embed(title="Listings", color=0xff0000)
            em_msg.add_field(
                name="Listings",
                value=f"No more listings found. (page {self.page})",
                inline=False)
            await interaction.followup.send(embed=em_msg)
        self.stop()

class AllLevelListings(discord.ui.View):
    def __init__(self, bot, building: str, level: int, page: int = 1):
        super().__init__()
        self.bot: Bot = bot
        self.page = page
        self.building = building
        self.level = level
        self.maxLevel = self.bot.data["maxLevel"]

    @discord.ui.button(label="More results", style=discord.ButtonStyle.green)
    async def more(self, interaction: discord.Interaction,
                   button: discord.ui.Button) -> None:
        await interaction.response.defer(thinking=True)
        building_name: str = self.building.rsplit("_", 1)[0]
        rarity: str = self.building.rsplit("_", 1)[1][0]
        self.page += 1
        listings = self.bot.api.get_listings(self.building, self.page)
        while not listings:
            if self.level < int(self.maxLevel[building_name][rarity]):
                self.page = 1
                self.building = self.building.replace(
                    rarity + str(self.level),
                    rarity + str(self.level+1))
                self.level += 1
                listings = self.bot.api.get_listings(self.building, self.page)
            else:
                em_msg = discord.Embed(title="Listings", color=0xff0000)
                em_msg.add_field(
                    name="Listings",
                    value=f"No more listings found.",
                    inline=False)
                await interaction.followup.send(embed=em_msg)
                return
        em_msg = discord.Embed(
            title="Listings",
            description=f"Listings containing {self.building} " +
                        f"(level {self.level}, page {self.page})",
            color=0x00ff00)

        _build_listings_embed(interaction, em_msg, listings)
        listing_view = AllLevelListings(self.bot, self.building,
                                        self.level, self.page)
        await interaction.followup.send(embed=em_msg,
                                        view=listing_view)
        self.stop()

def _build_listings_embed(
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
