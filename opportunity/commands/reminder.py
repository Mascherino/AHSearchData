import logging
import string

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Optional,
    List,
)

import discord
from discord import app_commands
from discord.ext import commands

from apscheduler.job import Job

from utils import Color

if TYPE_CHECKING:
    from opportunity.opportunity import Bot

class Reminder(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: Bot = bot
        self.logger = logging.getLogger("opportunity." + __name__)
        self.buildings = self.bot.api.get_building_names_clean()

    async def job_ac(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        job_name: str = interaction.namespace.job
        choices = []
        jobs: Optional[List[Job]]
        jobs = self.bot.scheduler.get_user_jobs(interaction.user.id)
        choices = []
        if jobs:
            choices = jobs
            if len(jobs) > 25:
                if len(job_name) >= 1:
                    choices = [s for s in choices
                               if job_name.lower() in s.kwargs["task_name"] or
                               job_name.lower() in s.id]
                if len(choices) > 25:
                    choices = []
        return [
            app_commands.Choice(
                name=f"{job.kwargs['task_name']} ({job.id})", value=job.id)
            for job in choices
            if current.lower() in job.kwargs["task_name"].lower()
        ]

    @app_commands.command()
    @app_commands.autocomplete(job=job_ac)
    async def delreminder(
        self,
        interaction: discord.Interaction,
        job: str
    ) -> None:
        jobc: Optional[Job] = self.bot.scheduler.get_job(job)
        if jobc:
            if jobc.kwargs["user"] == interaction.user.id:
                self.bot.scheduler.remove_job(job)
                em_msg = discord.Embed(
                    title="Reminders",
                    description=f"Successfully removed job " +
                                f"**{jobc.kwargs['task_name']}** with " +
                                f"id **{jobc.id}**",
                    color=Color.GREEN)
                await interaction.response.send_message(embed=em_msg)
            else:
                em_msg = discord.Embed(
                    title="Error",
                    description="You cannot remove a " +
                                "reminder from another user",
                    color=Color.RED)
                await interaction.response.send_message(embed=em_msg)

    @app_commands.command()
    async def reminders(
        self,
        interaction: discord.Interaction
    ) -> None:
        await interaction.response.defer(thinking=True)
        jobs: Optional[List[Job]] = self.bot.scheduler.get_user_jobs(
            interaction.user.id)
        em_msg = discord.Embed(
            title=f"Reminders for {interaction.user.display_name}",
            color=Color.GREEN)

        task_names = "\n".join([job.kwargs["task_name"] for job in jobs]
                               if jobs else ["-"])
        em_msg.add_field(name=f"Task", value=task_names)

        remind_time = "\n".join([
            str(job.next_run_time.replace(microsecond=0)) for job in jobs]
            if jobs else ["-"])
        em_msg.add_field(name="Due time", value=remind_time)

        ids = "\n".join([job.id for job in jobs] if jobs else ["-"])
        em_msg.add_field(name="ID", value=ids)

        await interaction.followup.send(embed=em_msg)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Reminder(bot))
