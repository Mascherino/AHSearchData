#!/usr/bin/env python

import argparse
import logging
import json
import os
from os.path import dirname as up
import os.path
import sys
import sqlite3

# Annotation imports
from typing import (
    Any,
    Dict,
)

if up(up(__file__)) not in sys.path:
    sys.path.append(up(up(__file__)))
    from opportunity.utils import setup_logging

def main(args, loglevel):
    setup_logging(
        "jsonToSQLite",
        log_path=os.path.join(up(up(__file__)), "logs", ".log"))
    logger = logging.getLogger("jsonToSQLite")
    logger.setLevel(loglevel)

    con = sqlite3.connect("opportunity.sqlite", isolation_level=None)
    logger.info(f"Connected to opportunity.sqlite")

    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS recipes")
    cur.execute("DROP TABLE IF EXISTS prep")
    cur.execute("VACUUM")  # reduce file size to data size

    cur.execute("CREATE TABLE recipes(id TEXT, name TEXT, " +
                "durationSeconds INT, inputs TEXT)")
    cur.execute("CREATE TABLE prep(category TEXT, recipes TEXT)")
    con.commit()

    j = {}
    file = os.path.join(args.data_folder, "recipes.json")
    with open(file, "r", encoding="utf-8") as f:
        logger.info(f"reading {os.path.basename(file)}...")
        try:
            j = json.load(f)
        except Exception as e:
            logger.error(e)

        for key in j:
            r = j[key]
            cur.execute("""INSERT INTO recipes VALUES(?, ?, ?, ?)""",
                        (r["id"],
                         r["name"],
                         r["durationSeconds"],
                         json.dumps(r["inputs"])))
    file = os.path.join(args.data_folder, "prepared.json")
    with open(file, "r", encoding="utf-8") as f:
        logger.info(f"reading {os.path.basename(file)}...")
        try:
            j: Dict[str, Dict[str, Any]] = json.load(f)
        except Exception as e:
            logger.error(e)
        for key in j:
            r = j[key]
            cur.execute("""INSERT INTO prep VALUES(?, ?)""",
                        (key, json.dumps(r)))

    con.commit()
    con.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert json to sqlite db")

    parser.add_argument(
        "data_folder",
        help="folder containing json files",
        metavar="data_folder")
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")
    args = parser.parse_args()

    loglevel = logging.DEBUG if args.verbose else logging.INFO

    main(args, loglevel)
