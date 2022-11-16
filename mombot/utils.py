from __future__ import annotations
import logging
import logging.handlers
import os
import sys
import json
import re
import string
import random

# Annotation imports
from typing import (
    Optional,
    Tuple,
    Dict,
    Any,
)
class LoggingHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, app_args: Dict[str, Any], **kwargs) -> None:
        super().__init__(app_args['log_file'], **kwargs)
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

def setup_logging(app_args: Dict[str, Any]
                  ) -> Tuple[logging.StreamHandler,
                             Optional[LoggingHandler],
                             Optional[str]]:
    root_logger = logging.getLogger()
    root_logger.setLevel(app_args.get("log_level", logging.INFO))
    stdout_handler = logging.StreamHandler(sys.stdout)
    format = logging.Formatter(
        '[%(filename)s:%(funcName)s()] - %(message)s')
    stdout_handler.setFormatter(format)
    warning: Optional[str] = None
    file_handler: Optional[LoggingHandler] = None
    log_file: str = app_args.get('log_file', "")
    if log_file:
        try:
            file_handler = LoggingHandler(
                app_args, when='midnight', backupCount=2)
            formatter = logging.Formatter(
                '%(asctime)s [%(filename)s:%(funcName)s()] - %(message)s')
            file_handler.setFormatter(formatter)
        except Exception:
            log_file = os.path.normpath(log_file)
            dir_name = os.path.dirname(log_file)
            warning = f"Unable to create log file at '{log_file}'. " \
                      f"Make sure that the folder '{dir_name}' exists. "
    return stdout_handler, file_handler, warning

def setup_logging_custom(app_args: Dict[str, Any]
                         ) -> Tuple[logging.StreamHandler,
                                    Optional[LoggingHandler]]:
    stdout_handler = logging.StreamHandler(sys.stdout)
    format = logging.Formatter(
        f'[{app_args.get("name","%(filename)")}] - %(message)s')
    stdout_handler.setFormatter(format)
    return stdout_handler, None

def prepare_recipes(input: str, output: str) -> None:
    with open(input, "r", encoding="utf-8") as fi:
        recipes: Dict[str, Any] = json.load(fi)
    processed_recipes = []
    for recipe in recipes.keys():
        if re.match(r".*_[C,U,R,E,L,M](10|[0-9])", recipe):
            if recipe.rsplit("_", 1)[0] not in processed_recipes:
                processed_recipes.append(recipe.rsplit("_", 1)[0])

def id_generator(size=6, chars=string.ascii_uppercase + string.digits +
                 string.ascii_lowercase) -> str:
    return ''.join(random.choice(chars) for _ in range(size))
