import logging

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

from utils import Color, abbr_to_full

if TYPE_CHECKING:
    from opportunity.opportunity import Bot

async def profession_ac(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    choices = [
        "Scavenging", "Life Science", "Electrical", "Mining",
        "Machining", "Fabrication", "Chemistry", "Robotics", "Aerospace"
    ]
    # professions to be released: Cooking, Entrepreneurship, Entertainment
    return [
        app_commands.Choice(name=profession, value=profession)
        for profession in choices if current.lower() in profession.lower()
    ]

class Train(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)
        self.train_data = self.bot.data["prepared"]["training_hall_1"]

    @app_commands.command()
    @app_commands.autocomplete(profession=profession_ac)
    async def train(
            self,
            interaction: discord.Interaction,
            profession: str,
            start: app_commands.Range[int, 1, 199],
            end: app_commands.Range[int, 2, 200],
    ) -> None:
        await interaction.response.defer(thinking=True)
        if end <= start:
            await interaction.followup.send(embed=discord.Embed(
                title="Error",
                description="End level must be higher than the start level",
                color=Color.RED))
            return
        if profession != "Aerospace" and (start > 149 or end > 150):
            await interaction.followup.send(embed=discord.Embed(
                title="Error",
                description="Currently only Aerospace can be " +
                            "trained above level 150",
                color=Color.RED))
            return
        self.logger.info(f"Iterating over levels {start} " +
                         f"to {end} for {profession}")
        profession_prep = profession.replace(" ", "").lower()
        profession_lv = profession_prep + "_Lv"
        currlvl = start+1
        result: Dict[str, Any] = {}
        while currlvl <= int(end):
            try:
                if profession == "Aerospace":
                    data = self.bot.data["prepared"]["ground-control-mission"]
                    curr = data[profession_lv + str(currlvl)]
                else:
                    curr = self.train_data[profession_lv + str(currlvl)]
                currinput = curr["inputs"]
                for item in currinput:
                    name = item["itemMatch"][0]
                    if name in ["energy", "dusk"] or \
                            "tool" in name or \
                            "research" in name:
                        if name not in result:
                            result[name] = item["quantity"]*10 \
                                if name == "energy" else item["quantity"]
                        else:
                            result[name] += item["quantity"]*10 \
                                if name == "energy" else item["quantity"]
            except KeyError:
                em_msg = discord.Embed(
                    title="Error",
                    description=f"No data found for " +
                                f"{profession} level {str(currlvl)}",
                    color=Color.RED)
                await interaction.followup.send(embed=em_msg)
                return
            currlvl += 1
        description = f"Requirements to train {profession} " + \
                      f"from {start} to {end}"
        em_msg = discord.Embed(
            title="Training",
            description=description,
            color=Color.GREEN)
        items = []
        for res in result.keys():
            s = res.rsplit("_", 1)
            emoji_name = profession.split(" ")
            if "research" in res:
                emoji_name.append("Research")
                emoji = "".join(emoji_name)
                items.append(
                    " ".join([self.bot.emoji[emoji],
                              abbr_to_full(s[len(s)-1]),
                              "Research"]))
            elif "tools" in res:
                emoji_name.append("Tools")
                emoji = "".join(emoji_name)
                items.append(
                    " ".join([self.bot.emoji[emoji],
                              "Sealed",
                              abbr_to_full(s[len(s)-1])
                              if profession != "Scavenging" else s[1],
                              "Tools"]))
            else:
                items.append(" ".join([self.bot.emoji[res.capitalize()],
                                       res.capitalize()]))
        em_msg.add_field(name="Items", value="\n".join(items))
        em_msg.add_field(name="Quantity",
                         value="\n".join([str(x) for x in result.values()]))
        await interaction.followup.send(embed=em_msg)

async def help() -> str:
    help_msg = """```
The train command is used to calculate
the amount of resources required to level
up a profession to a certain level

Input:
-------
profession - the profession you want to
             calculate the resources for
start - the level you start at [1-149]
end - the level you want to end at [2-150]

Output:
-------
Returns a list of resources needed for
leveling up from start to end ```
"""
    return help_msg

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Train(bot))
