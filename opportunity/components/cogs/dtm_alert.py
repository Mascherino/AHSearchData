import logging
import sqlite3

import discord
from discord.ext import commands
import datetime as dt

from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Dict,
    Any
)

from utils import Color, get_dtm_listings

if TYPE_CHECKING:
    from opportunity import Bot

class DTMAlert(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)
        self.logger.info("Starting DTMAlert cog")
        self.url = f"https://wax.api.atomicassets.io/atomicmarket/v2/" + \
                   f"sales?state=1&collection_name=onmars" + \
                   f"&schema_name=land.plots&immutable_data.quadrangle=" + \
                   f"Coprates&page=1&limit=100&order=asc&sort=price"
        self.bot.scheduler.add_job(
            self.alert,
            "interval",
            minutes=int(self.bot.config["dtmalert"]["interval"]),
            id="dtmalert",
            replace_existing=True,
            jobstore="memory")

        con = sqlite3.connect("opportunity.sqlite")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS dtm_alert(name TEXT, " +
                    "sale_id INT)")
        con.commit()
        con.close()

    async def alert(self) -> None:
        con = sqlite3.connect("opportunity.sqlite")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM dtm_alert")
        alreadyNotified = cur.fetchall()

        if not (listings := self.bot.api.get_custom_listings(self.url)):
            return
        listings = get_dtm_listings(listings)
        if not listings:
            return
        threshold = int(self.bot.config["dtmalert"]["threshold"])
        toBeNotified = []
        for listing in listings:
            notified = False
            if int(listings[listing]["price"]) <= threshold:
                self.logger.debug("Found listing below or equal to threshold")
                for alrNot in alreadyNotified:
                    lis = listings[listing]
                    link = lis["link"].rsplit("/", 1)[1]
                    if str(dict(alrNot)["sale_id"]) == link and \
                            dict(alrNot)["name"] == lis["name"]:
                        notified = True
                        break
                if notified:
                    self.logger.debug("Listing already notified, skipping")
                    continue
                toBeNotified.append(listings[listing])
                cur.execute("""INSERT INTO dtm_alert VALUES(?, ?)""",
                            (listings[listing]["name"],
                             listings[listing]["link"].rsplit("/", 1)[1]))
        if toBeNotified:
            em_msg = discord.Embed(
                title="DTM ALERT",
                color=Color.GREEN)
            # self.logger.debug(f"Listings to be notified {str(toBeNotified)}")
            for lis in toBeNotified:
                em_msg.add_field(
                    name=lis["name"],
                    value="\n".join([
                        f"[Link]({lis['link']})",
                        f"{str(lis['price'])} {lis['token_symbol']}"]))
            if not (ch_id := self.bot.config["dtmalert"]["channel_id"]):
                self.logger.error("No channel_id in config file")
            if isinstance(channel := self.bot.get_channel(int(ch_id)),
                          discord.TextChannel):
                await channel.send(embed=em_msg)
        else:
            self.logger.info("No new listings to notify")
        con.commit()
        con.close()
        return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DTMAlert(bot))
