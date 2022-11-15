#!/usr/bin/env python

import argparse
import logging
import json
import os

from utils import setup_logging

def main(args, loglevel):
    stdout_hdlr, file_hdlr, warn = setup_logging({
        "log_file": "split_json.log",
        "log_level": loglevel})
    logger = logging.getLogger()
    logger.addHandler(stdout_hdlr)
    if warn:
        logging.error(warn)
    else:
        logger.addHandler(file_hdlr)

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
    parser = argparse.ArgumentParser(description="Does a thing to some stuff.")

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

    # Set loglevel
    loglevel = logging.DEBUG if args.verbose else logging.INFO

    main(args, loglevel)
