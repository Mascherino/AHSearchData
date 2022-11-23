import discord
from discord.ext import commands, tasks
import datetime as dt

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Optional,
    Union
)

if TYPE_CHECKING:
    import opportunity

explorer_channel_id = 1038886699587076216
explorer_role_id = 1038880989662957660

hauler_channel_id = 0000
hauler_role_id = 0000

happyhour_channel_id = 1038446080540561428  # test
happyhour_role_id = 1039190550382919720  # HappyHour

explorer_channel: Optional[Union[
    discord.abc.GuildChannel, discord.Thread, discord.abc.PrivateChannel]]
explorer_role: Optional[discord.Role]

# hauler_channel
# hauler_role

happyhour_channel: Optional[Union[
    discord.abc.GuildChannel, discord.Thread, discord.abc.PrivateChannel]]
happyhour_role: Optional[discord.Role]

class Notifications(commands.Cog):

    def __init__(self, bot):
        self.index = 0
        self.bot: opportunity.Bot = bot
        self.bot.logger.info("Starting Notifications cog")

        self.explorer_begin.start()
        self.explorer_end.start()
        self.happyhour_start.start()
        self.happyhour_end.start()

        global explorer_channel
        global explorer_role
        # global hauler_channel
        # global hauler_role
        global happyhour_channel
        global happyhour_role

        explorer_channel = self.bot.get_channel(explorer_channel_id)
        if isinstance(explorer_channel, discord.abc.GuildChannel):
            explorer_role = discord.utils.get(
                explorer_channel.guild.roles, id=explorer_role_id)

        # hauler_channel = self.bot.get_channel(hauler_channel_id)
        # if isinstance(hauler_channel, discord.abc.GuildChannel):
        #     hauler_role = discord.utils.get(
        #         hauler_channel.guild.roles, id=hauler_role_id)

        happyhour_channel = self.bot.get_channel(happyhour_channel_id)
        if isinstance(happyhour_channel, discord.abc.GuildChannel):
            happyhour_role = discord.utils.get(
                happyhour_channel.guild.roles, id=happyhour_role_id)

    @tasks.loop(time=dt.time(1, 00, 00, tzinfo=dt.timezone(
        dt.timedelta(hours=1))))
    async def explorer_begin(self):
        if ((dt.datetime.now().isoweekday() == 1) or
                (dt.datetime.now().isoweekday() == 4)):
            ending = dt.datetime.now() + dt.timedelta(days=1)
            time = f"<t:{int(ending.timestamp())}:R>"
            if (isinstance(explorer_channel, discord.TextChannel) and
                    isinstance(explorer_role, discord.Role)):
                await explorer_channel.send(f"{explorer_role.mention}\n" +
                                            f"Explorer Missions are now " +
                                            f"available for 24 hours. " +
                                            f"Ending {time}",
                                            delete_after=(60*65*24))

    @tasks.loop(time=dt.time(0, 50, 00, tzinfo=dt.timezone(
        dt.timedelta(hours=1))))
    async def explorer_end(self):
        if ((dt.datetime.now().isoweekday() == 2) or
                (dt.datetime.now().isoweekday() == 5)):
            if (isinstance(explorer_channel, discord.TextChannel) and
                    isinstance(explorer_role, discord.Role)):
                await explorer_channel.send(f"{explorer_role.mention}\n" +
                                            "Explorer Missions are only " +
                                            "available for another 10 minutes.",
                                            delete_after=(60*15))

    @tasks.loop(time=dt.time(20, 3, 00, tzinfo=dt.timezone(
        dt.timedelta(hours=1))))
    async def happyhour_start(self):
        ending = dt.datetime.now() + \
            dt.timedelta(hours=3)
        time = f"<t:{int(ending.timestamp())}:R>"
        if (isinstance(happyhour_channel, discord.TextChannel) and
                isinstance(happyhour_role, discord.Role)):
            await happyhour_channel.send(f"{happyhour_role.mention}\n" +
                                         f"Happy hour is now available. " +
                                         f"Ending {time}",
                                         delete_after=(60*65*3))

    @tasks.loop(time=dt.time(22, 51, 00, tzinfo=dt.timezone(
        dt.timedelta(hours=1))))
    async def happyhour_end(self):
        if (isinstance(happyhour_channel, discord.TextChannel) and
                isinstance(happyhour_role, discord.Role)):
            await happyhour_channel.send(f"{happyhour_role.mention}\n" +
                                         "Happy Hour ends in 10 minutes.",
                                         delete_after=(60*15))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Notifications(bot))
