import logging

import discord
from discord.ext import commands
import datetime as dt

from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger

# Annotation imports
from typing import (
    TYPE_CHECKING
)

if TYPE_CHECKING:
    from opportunity.opportunity import Bot

class Notifications(commands.Cog):

    ex_ch_id = 1038886699587076216  # Explorer channel id
    ex2_r_id = 1038880989662957660  # 2x Explorer role id
    ex_r_id = 1065156457244405821  # 1x Explorer role id

    ha_ch_id = 1054020390114045985  # Hauler channel id
    ha_r_id = 1054020653247901868  # Hauler role id

    happy_ch_id = 1054011400583925792  # Happy Hour channel id
    happy_r_id = 1042527035467235500  # Happy Hour role id

    rp_ch_id = 00000  # Research paper channel id
    rp_r_id = 1074766817148555285  # Research paper role id

    triggers = {
        "hauler": CronTrigger(hour=12, minute=40, day_of_week="sun,wed"),
        "happyhour_start": OrTrigger([
            CronTrigger(hour=1, minute=0, day_of_week="sat,sun"),
            CronTrigger(hour=13, minute=0, day_of_week="sat,sun")]),
        "happyhour_end": OrTrigger([
            CronTrigger(hour=3, minute=50, day_of_week="sat,sun"),
            CronTrigger(hour=15, minute=50, day_of_week="sat,sun")]),
        "explorer_24h_before": CronTrigger(hour=1,
                                           minute=0,
                                           day_of_week="sun,wed"),
        "explorer_start": CronTrigger(hour=1, minute=0, day_of_week="mon,thu"),
        "explorer_end": CronTrigger(hour=0, minute=50, day_of_week="tue,fri"),
    }

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)
        self.logger.info("Starting Notifications cog")
        for func in [self.explorer_start, self.explorer_end, self.hauler,
                     self.happyhour_start, self.happyhour_end]:
            if trigger := self.triggers.get(str(func.__name__)):
                self.bot.scheduler.add_job(
                    func,
                    trigger=trigger,
                    jobstore="memory",
                    id=func.__name__,
                    replace_existing=True
                )

        if isinstance(ex_ch := self.bot.get_channel(self.ex_ch_id),
                      discord.abc.GuildChannel):
            self.ex_ch = ex_ch
            self.ex_r = discord.utils.get(ex_ch.guild.roles, id=self.ex_r_id)
            self.ex2_r = discord.utils.get(ex_ch.guild.roles, id=self.ex2_r_id)

        if isinstance(ha_ch := self.bot.get_channel(self.ha_ch_id),
                      discord.abc.GuildChannel):
            self.ha_ch = ha_ch
            self.ha_r = discord.utils.get(ha_ch.guild.roles, id=self.ha_r_id)

        if isinstance(hh_ch := self.bot.get_channel(self.happy_ch_id),
                      discord.abc.GuildChannel):
            self.happy_ch = hh_ch
            self.happy_r = discord.utils.get(hh_ch.guild.roles,
                                             id=self.happy_r_id)

    async def explorer_24h_before(self) -> None:
        if (isinstance(self.ex_ch, discord.TextChannel) and
                isinstance(self.ex2_r, discord.Role)):
            await self.ex_ch.send(f"{self.ex2_r.mention}\n" +
                                  f"Explorer Missions will be" +
                                  f"available in 24 hours. " +
                                  f"Make sure to plan accordingly.")

    async def explorer_start(self) -> None:
        ending = dt.datetime.now() + dt.timedelta(days=1)
        time = f"<t:{int(ending.timestamp())}:R>"
        if (isinstance(self.ex_ch, discord.TextChannel) and
                isinstance(self.ex_r, discord.Role) and
                isinstance(self.ex2_r, discord.Role)):
            await self.ex_ch.send(f"{self.ex_r.mention} {self.ex2_r.mention}" +
                                  f"\nExplorer Missions are now " +
                                  f"available for 24 hours. " +
                                  f"Ending {time}")

    async def explorer_end(self) -> None:
        if (isinstance(self.ex_ch, discord.TextChannel) and
                isinstance(self.ex_r, discord.Role) and
                isinstance(self.ex2_r, discord.Role)):
            await self.ex_ch.send(f"{self.ex_r.mention} {self.ex2_r.mention}" +
                                  "\nExplorer Missions are only " +
                                  "available for another 10 minutes.")

    async def hauler(self) -> None:
        if (isinstance(self.ha_ch, discord.TextChannel) and
                isinstance(self.ha_r, discord.Role)):
            await self.ha_ch.send(f"{self.ha_r.mention}\n" +
                                  "Do not start any hauler missions " +
                                  "to leave slots for explorers open")

    async def happyhour_start(self) -> None:
        ending = dt.datetime.now() + dt.timedelta(hours=3)
        time = f"<t:{int(ending.timestamp())}:R>"
        if (isinstance(self.happy_ch, discord.TextChannel) and
                isinstance(self.happy_r, discord.Role)):
            await self.happy_ch.send(f"{self.happy_r.mention}\n" +
                                     f"Happy hour is now available " +
                                     f"for 3 hours")

    async def happyhour_end(self) -> None:
        if (isinstance(self.happy_ch, discord.TextChannel) and
                isinstance(self.happy_r, discord.Role)):
            await self.happy_ch.send(f"{self.happy_r.mention}\n" +
                                     "Happy Hour ends in 10 minutes.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Notifications(bot))
