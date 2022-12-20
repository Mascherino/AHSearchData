#!/usr/bin/env python

import argparse
import logging
import json
import os
from os.path import dirname as up
import sys

# Annotation imports
from typing import (
    Any,
    Dict,
)

if up(up(__file__)) not in sys.path:
    sys.path.append(up(up(__file__)))
    from opportunity.utils import setup_logging

def main(args):
    setup_logging(
        "reduce",
        log_path=os.path.join(up(up(__file__)), "logs", ".log"))
    logger = logging.getLogger("reduce")

    j: Dict[str, Any] = {}
    with open(args.recipe_file, "r", encoding="utf-8") as f:
        logger.info(f"reading {args.recipe_file}...")
        try:
            j = json.load(f)
        except Exception as e:
            logger.error(e)
        for key in list(j.keys()):
            for attr in list(j[key]):
                if attr not in ["id", "name", "durationSeconds",
                                "requirements", "inputs"]:
                    del j[key][attr]
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                logger.info(f"Writing {args.output}")
                json.dump(j, f)
                logger.info(f"Successfully written {args.output}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Reduce 'recipes.json' size.")

    parser.add_argument(
        "recipe_file",
        help="JSON file to reduce",
        metavar="recipe_file")
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")
    parser.add_argument(
        "-o",
        "--output",
        help="output folder",
        default="")
    args = parser.parse_args()

    main(args)
