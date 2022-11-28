from __future__ import annotations
import logging
import logging.handlers
import os
import sys
import json
import re
import string
import random

from enum import IntEnum

# Annotation imports
from typing import (
    Optional,
    Tuple,
    Dict,
    Any,
)

def translate_bldg(building: str):
    translate = {
        "solar_panel": "solar",
        "greenhouse": "greenhouse",
        "water_filter": "water_filter",
        "cad": "cad",
        "grindnbrew": "gnb",
        "polar_workshop": "polar",
        "mining_rig": "mining",
        "machine_shop": "machine",
        "chem_lab": "chem_lab",
        "3d_print_shop": "3d_print",
        "smelter": "smelter",
        "sab_reactor": "sab",
        "rover_works": "rover_works",
        "engineering_bay": "engineering",
        "concrete_habitat": "concrete_habitat",
        "shelter": "shelter",
        "thorium-reactor": "reactor",
        "cantina": "cantina_gig",
        "training_hall": "training_hall",
        "bazaar": "bazaar",
        "teashop": "teashop",
        "gallery": "gallery"
    }
    return translate[building]

class LoggingHandler(logging.handlers.TimedRotatingFileHandler):

    def __init__(self, log_file: str) -> None:
        super().__init__(log_file)
        self.rollover_info: Dict[str, str] = {
            'header': f"{'-'*20}Log Start{'-'*20}"
        }
        lines = [line for line in self.rollover_info.values() if line]
        if self.stream is not None:
            self.stream.write("\n".join(lines) + "\n")

    def set_rollover_info(self, name: str, item: str) -> None:
        self.rollover_info[name] = item

    def doRollover(self) -> None:
        super().doRollover()
        lines = [line for line in self.rollover_info.values() if line]
        if self.stream is not None:
            self.stream.write("\n".join(lines) + "\n")

class ColorFormatter(logging.Formatter):

    # \x1b[XXXm where XXX is a separated list of commands
    # 30-37 black, red, green, yellow, blue, magenta, cyan and white
    # 40-47 same except for the background
    # 90-97 same but "bright" foreground
    # 100-107 same as bright but for background.
    # 1 is bold, 2 is dim, 0 is reset, 4 is underlined.

    LEVEL_COLOURS = [
        (logging.DEBUG, '\x1b[40;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31m'),
        (logging.CRITICAL, '\x1b[41m'),
    ]

    FORMATS = {
        level: logging.Formatter(
            f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s' +
            f'\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s',
            '%Y-%m-%d %H:%M:%S',
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        record.exc_text = None
        return output

def setup_logging(
    name: str,
    handler: Optional[logging.Handler] = None,
    formatter: Optional[logging.Formatter] = None,
    level: int = -1,
    root: Optional[bool] = None,
    log_path: Optional[str] = None
) -> None:

    if level == -1:
        level = logging.DEBUG

    if handler is None:
        handler = logging.StreamHandler()

    if formatter is None:
        if isinstance(handler, logging.StreamHandler):
            formatter = ColorFormatter()
        else:
            dt_fmt = '%Y-%m-%d %H:%M:%S'
            fmt = '[{asctime}] [{levelname:<8}] {name}: {message}'
            formatter = logging.Formatter(fmt, dt_fmt, style='{')

    file_handler = None
    if root:
        logger = logging.getLogger()

        if log_path:
            file_handler = LoggingHandler(log_path)
            dt_fmt = '%Y-%m-%d %H:%M:%S'
            fmt = '[{asctime}] [{levelname:<8}] {name}: {message}'
            file_formatter = logging.Formatter(fmt, dt_fmt, style='{')
            file_handler.setFormatter(file_formatter)
    else:
        # library, _, _ = name.partition('.')
        logger = logging.getLogger(name)

    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)
    if file_handler:
        logger.addHandler(file_handler)

def prepare_recipes(input: str, output: str) -> None:
    with open(input, "r", encoding="utf-8") as fi:
        recipes: Dict[str, Any] = json.load(fi)
    processed_recipes = []
    for recipe in recipes.keys():
        if re.match(r".*_[C,U,R,E,L,M](10|[0-9])", recipe):
            if recipe.rsplit("_", 1)[0] not in processed_recipes:
                processed_recipes.append(recipe.rsplit("_", 1)[0])

def id_generator(size=6, chars=string.ascii_letters + string.digits) -> str:
    return ''.join(random.choice(chars) for _ in range(size))

class Color(IntEnum):
    RED = 0xff0000
    GREEN = 0x00ff00
    BLUE = 0x0000ff
    DARK_GRAY = 0x424949
