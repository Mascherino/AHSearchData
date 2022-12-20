#!/usr/bin/env python

import argparse
import logging
import json
import os
from os.path import dirname as up
import re
import sys
from collections import defaultdict

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
        "prepare_recipes",
        log_path=os.path.join(up(up(__file__)), "logs", ".log"))
    logger = logging.getLogger("prepare_recipes")

    j: Dict[str, Any] = {}
    with open(args.json, "r", encoding="utf-8") as f:
        logger.info(f"reading {args.json}...")
        try:
            j = json.load(f)
        except Exception as e:
            logger.error(e)
        recipes = {}
        categories = defaultdict(dict)
        for recipe in j:
            if len(recipe.rsplit("_", 1)) > 1:
                s = recipe.rsplit("_", 1)
                try:
                    if re.match(r'C(10|[0-9])', s[len(s)-1]):
                        if recipe not in categories[j[recipe]["category"]]:
                            categories.setdefault(j[recipe]["category"], {})
                            category = j[recipe]["category"]
                            r = {k: v for k, v in j[recipe].items() if k in
                                 ["id", "name", "durationSeconds",
                                  "requirements", "inputs"]}
                            categories[category][recipe] = r
                    if "Lv" in s[len(s)-1] or \
                            "prepare" in s[0] or \
                            "host" in s[0] or \
                            "restore" in s[0] or \
                            "tea" in s[0]:
                        if recipe not in categories[j[recipe]["category"]]:
                            category = j[recipe]["category"]
                            categories.setdefault(j[recipe]["category"], {})
                            a = j[recipe]
                            r = {k: v for k, v in j[recipe].items() if k in
                                 ["id", "name", "durationSeconds",
                                  "requirements", "inputs"]}
                            categories[category][recipe] = r
                except Exception as e:
                    logger.error(e)
            else:
                categories.setdefault(j[recipe]["category"], {})
                categories[j[recipe]["category"]][recipe] = j[recipe]
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                logger.info(f"Writing {args.output}")
                json.dump(categories, f)
                logger.info(f"Successfully written {args.output}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Split json into its keys.")

    parser.add_argument(
        "json",
        help="JSON file to split",
        metavar="json")
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
