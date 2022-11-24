import json
from json.decoder import JSONDecodeError
import os
from os.path import dirname as up
import re

import datetime as dt
import logging
import configparser

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Dict,
    Sequence,
    Union
)

# Discord imports
import discord
from discord.ext import commands

# Custom modules
from components.views import Listings
from components.api import API
from components.scheduler import Scheduler
from utils import id_generator, setup_logging, Color

from apscheduler.job import Job

from apscheduler.jobstores.base import ConflictingIdError, JobLookupError

building_regex = r"(([a-zA-Z0-9_]+-gen[2,3]_)|(([a-zA-Z0-9]+-){0,1}" \
    r"([a-zA-Z0-9]+_){1,3})|([a-zA-Z0-9_]+-22_))[C,U,R,E,L,M,S](10|[1-9])"

config = configparser.ConfigParser()
root_path = up(up(__file__))
config_path = os.path.join(root_path, "config.cfg")
config.read(config_path)

class Bot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('!'),
                         intents=intents)

        self.logger = logging.getLogger("opportunity.bot")
        log_path = os.path.join(root_path, "logs", "opportunity.log")
        setup_logging("opportunity", root=True, log_path=log_path)
        logging.getLogger("discord").propagate = False

        self.config = config

        self.recipes = read_json(self, os.path.join(
            root_path,
            self.config["misc"]["json_folder"],
            "recipes.json"))

        self.scheduler: Scheduler = Scheduler(
            self.config['mariadb']['credentials'])
        self.scheduler.start()

        self.api: API = API(self)

    async def on_ready(self):

        if self.user:
            self.logger.info(f'Logged in as {self.user} (ID: {self.user.id})')

        await self.change_presence(activity=discord.Game(
                                   name="Million on Mars"))

        await load_cogs(self)
        await load_commands(self)
        await self.tree.sync()


''' Variables '''

data: Dict[str, str] = {}

''' Functions '''

async def load_cogs(bot: Bot) -> None:
    components_path = os.path.join(root_path, "mombot", "components", "cogs")
    for component in os.listdir(components_path):
        if os.path.isfile(os.path.join(components_path, component)):
            try:
                await bot.load_extension("components.cogs." + component[:-3])
                bot.logger.info(f"Successfully loaded '{component[:-3]}'")
            except Exception as e:
                bot.logger.error(e)

async def load_commands(bot: Bot) -> None:
    commands_path = os.path.join(root_path, "mombot", "commands")
    for command in os.listdir(commands_path):
        if os.path.isfile(os.path.join(commands_path, command)):
            try:
                await bot.load_extension("commands." + command[:-3])
                bot.logger.info(f"Successfully loaded command '{command[:-3]}")
            except Exception as e:
                bot.logger.error(e)

def read_json(bot: Bot, file: str) -> Optional[Dict[str, Any]]:
    ''' Read JSON config file and return it '''
    if os.path.isfile(file):
        if os.path.getsize(file) > 0:
            with open(file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    filename = os.path.basename(file)
                    bot.logger.info(f"Successfully read file '{filename}'")
                except JSONDecodeError:
                    data = {}
                    bot.logger.error(f"Error reading file {file}.")
        else:
            bot.logger.info(f"Successfully read empty file {file}.")
            return {}
        return data
    return None

def save_json(bot: Bot, file: str, data: Dict[str, Any]) -> None:
    ''' Save data variable as JSON config file '''
    if os.path.isfile(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, sort_keys=True, indent=4)
        bot.logger.info(f"Successfully saved file {file}.")

async def print_general_usage(ctx: commands.Context) -> None:
    await ctx.send(f'''General usage: Not Implemented''')  # TODO Implement

async def print_error(ctx: commands.Context, error: Any) -> None:
    await ctx.send(content=f"Error: {error}")

async def edit_msg_to_error(msg: discord.Message, error: Any) -> None:
    await msg.edit(content=error)

bot = Bot()

@bot.command(name="ah", aliases=["search", "atomichub"])
async def ah(ctx: commands.Context, name: str, rarity: str = "") -> None:
    '''
    Search AtomicHub marketplace

    Parameters:
        building (str): name of building

    Returns:
        Nothing, message is sent in channel
    '''
    got_listings = False
    amount = 1
    error = f"{name} did not match the required scheme."
    listings: Optional[Dict[Union[str, int], Any]] = None
    try:
        message = await ctx.send(ctx.author.mention + "\nGetting listings...")
        regex = re.compile("".join([building_regex, r"=[0-9]{0,1}"]))
        if re.match(regex, name):
            amount = int(name[-1])
            name = name[:-2]
            listings = bot.api.get_listings(name, 1, amount)
            got_listings = True
        elif re.match(building_regex, name):
            pass
        elif rarity is not None:
            name = f"{name}_{rarity.upper()}"
            if re.match(r'(([a-zA-Z0-9_]+-gen[2,3]_)|(([a-zA-Z0-9]+-){0,1}' +
                        '([a-zA-Z0-9]+_){1,3})|([a-zA-Z0-9_]+-22_))' +
                        '[C,U,R,E,L,M,S](10|[1-9])', name):
                pass
            else:
                await edit_msg_to_error(message, error)
                return
        else:
            await edit_msg_to_error(message, error)
            return
        if not got_listings:
            listings = \
                bot.api.get_listings(name, 1, 1)
        if listings:
            description = f"Listings containing {amount} {name} (page 1)"
            em_msg = discord.Embed(
                title="Listings",
                description=description,
                color=Color.GREEN)

            em_msg.add_field(
                name="Listings",
                value="\n".join([
                    listings[item]["link"] for item in listings.keys()]),
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
            # em_msg.add_field(
            # name="Building(s)",
            # value="\n".join([str(listings[item]["land"]["buildings"].keys())
            # for item in listings.keys()]), inline=True)
            await message.delete()
            view = Listings(name, 1)
            msg = await ctx.send(ctx.author.mention, embed=em_msg, view=view)
        else:
            error = f"Could not find any listings matching {name} with " + \
                    f"amount {amount}.\nMaybe try using a building from " + \
                    f"!buildings with rarity from !level ."
            await ctx.send(error)
    except Exception as e:
        print(e)
        await ctx.send(f"Could not search AH.\n{e}")

@ah.error
async def ah_error(ctx: commands.Context, err: commands.CommandError) -> None:
    if isinstance(err, commands.MissingRequiredArgument):
        await print_general_usage(ctx)
    elif isinstance(err, commands.CheckFailure):
        await ctx.send('You dont have the permission to use that command')

@bot.command(name="buildings", aliases=["bldg", "building"])
async def buildings(ctx: commands.Context):
    '''
    List all buildings

    Returns:
        Nothing, message is sent in channel
    '''
    try:
        msg = await ctx.send(ctx.author.mention + """\nGetting buildings..""")
        buildings: Optional[Dict[str, Any]] = bot.api.get_buildings()
        if buildings:
            bldg_list: Optional[Sequence[Any]] = bot.api.extract_data(
                buildings, "name")
            factories = []
            artifacts = []
            if bldg_list:
                for item in bldg_list:
                    if item not in ["total_space", "available_space"]:
                        name = item.rsplit("_", 1)
                        if len(name) > 1:
                            if name[1] == "A":
                                if not name[0] in artifacts:
                                    artifacts.append(name[0])
                            else:
                                if not name[0] in factories:
                                    factories.append(name[0])
            description = "List of all buildings"
            em_msg = discord.Embed(title="Buildings", description=description,
                                   color=Color.GREEN)
            em_msg.add_field(name="Factories", value="\n".join(factories),
                             inline=True)
            em_msg.add_field(name="Artifacts", value="\n".join(artifacts),
                             inline=True)
            await msg.delete()
            msg = await ctx.send(ctx.author.mention, embed=em_msg)
    except Exception as e:
        print(e)
        await ctx.send(f"Error listing all buildings.\n{e}")

@buildings.error
async def buildings_error(ctx: commands.Context, err: commands.CommandError):
    if isinstance(err, commands.CheckFailure):
        await ctx.send('You dont have the permission to use that command')

@bot.command(name="level", aliases=["levels", "lvl", "maxlevel"])
async def level(ctx: commands.Context):
    '''
    List all building level

    Returns:
        Nothing, message is sent in channel
    '''
    try:
        message = await ctx.send(ctx.author.mention + """\nGetting level..""")

        mythic = "C-M"
        special = "S"
        other_lvl = "10 (C), 8 (U), 6 (R), 5 (E-M)"
        buildings = {
            "solar_panel": {"rarities": mythic, "max_level": "10"},
            "cad": {"rarities": mythic, "max_level": "10"},
            "greenhouse": {"rarities": mythic, "max_level": "10"},
            "water_filter": {"rarities": mythic, "max_level": "10"},
            "grindnbrew": {"rarities": mythic, "max_level": "10"},
            "polar_workshop": {"rarities": mythic, "max_level": "10"},
            "mining_rig": {"rarities": mythic, "max_level": "10"},
            "smelter": {"rarities": mythic, "max_level": "10"},
            "machine_shop": {"rarities": mythic, "max_level": "10"},
            "sab_reactor": {"rarities": mythic, "max_level": "10"},
            "chem_lab": {"rarities": mythic, "max_level": "10"},
            "3d_print_shop": {"rarities": mythic, "max_level": "10"},
            "rover_works": {"rarities": mythic, "max_level": other_lvl},
            "cantina": {"rarities": special, "max_level": "6"},
            "bazaar": {"rarities": special, "max_level": "5"},
            "teashop": {"rarities": special, "max_level": "5"},
            "pirate_radio": {"rarities": special, "max_level": "10"},
            "library": {"rarities": special, "max_level": "10"},
            "training_hall": {"rarities": special, "max_level": "10"},
            "engineering_bay": {"rarities": mythic, "max_level": other_lvl},
            "concrete_habitat": {"rarities": mythic, "max_level": "5"},
            "shelter": {"rarities": mythic, "max_level": "5"},
            "gallery": {"rarities": special, "max_level": "10"},
            "metis_shield": {"rarities": mythic, "max_level": "1"},
            "thorium_reactor": {"rarities": mythic, "max_level": other_lvl}}
        rarities = ["C-M"]
        em_msg = discord.Embed(title="Buildings",
                               description="List of all buildings\n" +
                               "Possible rarities: C, U, R, E, L, M",
                               color=Color.GREEN)
        em_msg.add_field(name="Buildings",
                         value="\n".join(buildings.keys()), inline=True)
        em_msg.add_field(name="Rarities",
                         value="\n".join([
                             buildings[x]["rarities"] for x in buildings]),
                         inline=True)
        em_msg.add_field(name="Level",
                         value="\n".join([buildings[x]["max_level"]
                                         for x in buildings]),
                         inline=True)
        await message.delete()
        message = await ctx.send(ctx.author.mention, embed=em_msg)
    except Exception as e:
        print(e)
        await ctx.send(f"Error listing all level.\n {e}")


@bot.command(name="test")
async def test(ctx: commands.Context):
    bot.scheduler.add_job(
        remind,
        "date",
        next_run_time=dt.datetime.now()+dt.timedelta(seconds=10),
        kwargs={"user": ctx.author.id, "channel_id": ctx.channel.id})

async def remind(user: int, channel_id: int, **kwargs):
    channel = bot.get_channel(channel_id)
    u: discord.User = await bot.fetch_user(user)
    em_msg = discord.Embed(title="tasks ready")
    if isinstance(channel, discord.TextChannel):
        await channel.send(content=f"{u.mention}", embed=em_msg)

@bot.command(name="start", aliases=["addreminder"])
async def start(ctx: commands.Context, task: str) -> None:
    if bot.recipes:
        try:
            task_dir = bot.recipes[task]
        except KeyError as e:
            bot.logger.error(f"{task} key not found in recipes.")
            await ctx.send(f"{task} not found in recipes.")
            return
        job_id = id_generator(8)
        for _ in range(0, 100):
            try:
                bot.scheduler.add_job(
                    remind,
                    id=job_id,
                    trigger="date",
                    next_run_time=dt.datetime.now()+dt.timedelta(
                        seconds=task_dir["durationSeconds"]),
                    kwargs={
                        "user": ctx.author.id,
                        "channel_id": ctx.channel.id,
                        "task_name": task_dir["name"]})
            except ConflictingIdError as e:
                bot.logger.error("Conflicting id in job")
            break
        task_time = task_dir["durationSeconds"]
        m, s = divmod(task_time, 60)
        h, m = divmod(m, 60)
        task_time = '{:0>2}:{:0>2}:{:0>2}'.format(h, m, s)
        message = f"I'll remind you in {task_time} to " + \
                  f"finish your {task_dir['name']} task(s)"
        em_msg = discord.Embed(color=Color.DARK_GRAY)
        em_msg.add_field(name="Recipes", value=message)
        await ctx.send(embed=em_msg, ephemeral=True)

@bot.command(name="delreminder", aliases=["stop"])
async def delreminder(ctx: commands.Context, job_id: str) -> None:
    job: Optional[Job] = bot.scheduler.get_job(job_id)
    if isinstance(job, Job):
        if job.kwargs["user"] == ctx.author.id:
            bot.scheduler.remove_job(job_id)
            await ctx.send(f"Successfully removed job with id {job_id}")
        else:
            await ctx.send(f"You cannot remove a reminder from another user")
    else:
        bot.logger.error(f"Could not find job with id {job_id}")
        await ctx.send(f"Could not find reminder with id {job_id}")

@bot.command(name="reminders", aliases=["reminder"])
async def reminders(ctx: commands.Context) -> None:
    jobs: Optional[Sequence[Job]] = bot.scheduler.get_user_jobs(ctx.author.id)
    em_msg = discord.Embed(title=f"Reminders for {ctx.author.display_name}",
                           color=Color.DARK_GRAY)

    task_names = "\n".join([job.kwargs["task_name"] for job in jobs]
                           if jobs else ["-"])
    em_msg.add_field(name=f"Task", value=task_names)

    remind_time = "\n".join([
        str(job.next_run_time.replace(microsecond=0)) for job in jobs]
        if jobs else ["-"])
    em_msg.add_field(name="Due time", value=remind_time)

    ids = "\n".join([job.id for job in jobs] if jobs else ["-"])
    em_msg.add_field(name="ID", value=ids)

    await ctx.send(embed=em_msg)

@bot.command(name="tasks", aliases=["recipes"])
async def tasks(ctx: commands.Context) -> None:
    msg = f"A complete list of all recipes is available at " + \
        config["misc"]["recipes_url"]
    em_msg = discord.Embed(color=Color.DARK_GRAY)
    em_msg.add_field(name="Recipes", value=msg)
    await ctx.send(embed=em_msg)

bot.run(config["discord"]["TOKEN"])
