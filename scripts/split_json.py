#!/usr/bin/env python

import argparse
import logging
import json
import os
from os.path import dirname as up

from opportunity.utils import setup_logging

def main(args):
    setup_logging(
        "split_json",
        log_path=os.path.join(up(up(__file__)), "logs", "split_json.log"))
    logger = logging.getLogger("split_json")

    j = {}
    with open(args.json, "r", encoding="utf-8") as f:
        logging.info(f"reading {args.json}...")
        try:
            j = json.load(f)
        except Exception as e:
            logging.error(e)
        if args.output and not os.path.isdir(args.output):
            logging.info(f"dir {args.output} does not exist. Creating...")
            try:
                os.mkdir(args.output)
            except OSError as e:
                logging.error(e)
        for category in j.keys():
            path = os.path.join(args.output, category+".json")
            logging.info(f"Writing {category+'.json'}, path: {path}...")
            with open(path, "w", encoding="utf-8") as x:
                json.dump(j[category], x)
            logging.info(f"Successfully written {path}.")


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
