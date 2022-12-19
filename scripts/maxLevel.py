#!/usr/bin/env python

import argparse
import logging
import json
import os
from os.path import dirname as up
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
        "maxLevel",
        log_path=os.path.join(up(up(__file__)), "logs", ".log"))
    logger = logging.getLogger("maxLevel")

    j: Dict[str, Any] = {}
    with open(args.json, "r", encoding="utf-8") as f:
        logger.info(f"reading {args.json}...")
        try:
            j = json.load(f)
        except Exception as e:
            logger.error(e)
        maxLevel = defaultdict(dict)
        for building in j:
            name = building.rsplit("_", 1)[0]
            rlvl = building.rsplit("_", 1)[1]
            maxLevel[name][rlvl[0]] = rlvl[1] if len(rlvl) == 2 else rlvl[1:]
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                logger.info(f"Writing {args.output}")
                json.dump(maxLevel, f)
                logger.info(f"Successfully written {args.output}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract max level")

    parser.add_argument(
        "json",
        help="JSON file containing building data",
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
