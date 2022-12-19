#!/usr/bin/env python

import argparse
import logging
import json
import os
from os.path import dirname as up

def main(args):
    logger = logging.getLogger("split_json")

    j = {}
    with open(args.json, "r", encoding="utf-8") as f:
        logger.info(f"reading {args.json}...")
        try:
            j = json.load(f)
        except Exception as e:
            logger.error(e)
        if args.output and not os.path.isdir(args.output):
            logger.info(f"dir {args.output} does not exist. Creating...")
            try:
                os.mkdir(args.output)
            except OSError as e:
                logger.error(e)
        for category in j.keys():
            path = os.path.join(args.output, category+".json")
            logger.info(f"Writing {category+'.json'}, path: {path}...")
            with open(path, "w", encoding="utf-8") as x:
                json.dump(j[category], x)
            logger.info(f"Successfully written {path}.")


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
