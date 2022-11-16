import discord

from api import API
import configparser

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
        api = API(config["yourls"]["secret"])
        await interaction.response.defer(thinking=True)
        self.page += 1
        listings = api.get_listings(self.building, self.page)
        if listings:
            em_msg = discord.Embed(
                title="Listings",
                description=f"Listings containing {self.building} " +
                            f"(page {self.page})",
                color=0x00ff00)

            em_msg.add_field(
                name="Listings",
                value="\n".join([
                    listings[item]["link"] for item in listings.keys()]),
                inline=True)

            em_msg.add_field(
                name="Cost",
                value="\n".join([
                    str(listings[item]["price"]) + " " +
                    listings[item]["token_symbol"]
                    for item in listings.keys()]),
                inline=True)

            em_msg.add_field(
                name="Land(s)",
                value="\n".join([
                    listings[item]["land"]["rarity"]
                    if isinstance(listings[item]["land"], dict)
                    else "Bundle" for item in listings.keys()]),
                inline=True)
            listing_view = Listings(self.building, self.page)
            await interaction.followup.send(embed=em_msg,
                                            view=listing_view)
        else:
            em_msg = discord.Embed(title="Listings", color=0x00ff00)
            em_msg.add_field(
                name="Listings",
                value=f"No more listings found. (page {self.page})",
                inline=False)
            await interaction.followup.send(embed=em_msg)
        self.stop()
