import logging
import psutil
import datetime as dt

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

class Botinfo(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)

    @app_commands.command(description="Get detailed information" +
                                      " about the bot")
    async def botinfo(
            self,
            interaction: discord.Interaction,
    ) -> None:
        await interaction.response.defer(thinking=True)

        stats = {}
        process: psutil.Process = psutil.Process()
        cr_t: float = process.create_time()
        td: dt.timedelta = dt.datetime.now() - \
            dt.datetime.fromtimestamp(cr_t)
        minutes, seconds = divmod(td.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days = td.days
        stats["Uptime"] = f"{days}d, {hours}h, {minutes}m, {seconds}s"
        stats["Created at"] = "25.10.2022"
        stats["Latency"] = f"{round(self.bot.latency * 1000, 2)} ms"
        stats["discord.py Version"] = f"V {discord.__version__}"

        em_msg = discord.Embed(
            title=f"Opportunity information and statistics",
            color=Color.GREEN)
        for stat in stats.keys():
            em_msg.add_field(name=stat, value=stats[stat])
        em_msg.set_footer(text="Made by Maschs#6651")

        await interaction.followup.send(embed=em_msg)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Botinfo(bot))
