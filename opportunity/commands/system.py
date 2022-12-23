import logging
import psutil
import platform
import datetime as dt

# Annotation imports
from typing import (
    TYPE_CHECKING,
)

from discord import Embed
from discord import Interaction
from discord import app_commands
from discord.ext import commands

from utils import Color

if TYPE_CHECKING:
    from opportunity.opportunity import Bot

class System(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)

    @app_commands.command(description="Get detailed information" +
                                      " about the system the bot runs on")
    async def system(
            self,
            interaction: Interaction,
    ) -> None:
        await interaction.response.defer(thinking=True)

        stats = {}
        td: dt.timedelta = dt.datetime.now() - \
            dt.datetime.fromtimestamp(psutil.boot_time())
        minutes, seconds = divmod(td.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days = td.days
        stats["Uptime"] = f"{days}d, {hours}h, {minutes}m, {seconds}s"

        total_ram = round(int(psutil.virtual_memory().total / (1024 * 1024)))
        stats["Total_RAM"] = f"{total_ram} MB"

        free_ram = round(int(psutil.virtual_memory().available / (1024 * 1024)))
        stats["Free_RAM"] = f"{free_ram} MB"
        stats["Load_avg"] = psutil.getloadavg()[0] / psutil.cpu_count() * 100
        stats["CPU_count"] = psutil.cpu_count()
        stats["OS"] = platform.system()

        em_msg = Embed(
            title=f"Opportunity server system information",
            color=Color.GREEN)
        for stat in stats.keys():
            em_msg.add_field(name=stat.replace("_", " "), value=stats[stat])
        em_msg.set_footer(text="Made by Maschs#6651")

        await interaction.followup.send(embed=em_msg)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(System(bot))
