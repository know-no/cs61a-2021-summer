import argparse
import json
import os
from difflib import unified_diff

import local_server
import log
from formatter import prettify


def reformat_files(src, dest=None, check=False):
    if dest is None:
        dest = src
    with open(src) as src:
        original = src.read()
        formatted = prettify([original]) + "\n"
    if check:
        if original != formatted:
            print(
                "\n".join(
                    unified_diff(
                        original.splitlines(),
                        formatted.splitlines(),
                        fromfile="Original",
                        tofile="Formatted",
                    )
                )
            )
            exit(1)
    with open(dest, "w") as dest:
        dest.write(formatted)
    exit()


parser = argparse.ArgumentParser(description="CS61A Scheme Editor - Spring 2021")

parser.add_argument(
    "-f",
    "--files",
    type=argparse.FileType("r+"),
    help="Scheme files to test",
    metavar="FILE",
    nargs="*",
)
parser.add_argument(
    "-nb", "--nobrowser", help="Do not open a new browser window.", action="store_true"
)
parser.add_argument(
    "-n", "--no-dotted", help="Disable dotted lists", action="store_true"
)
parser.add_argument(
    "-p", "--port", type=int, default=31415, help="Choose the port to access the editor"
)
parser.add_argument(
    "-r",
    "--reformat",
    type=str,
    nargs="*",
    help="Reformats file and writes to second argument, if exists, or in-place, otherwise.",
    metavar="FILE",
)
parser.add_argument(
    "-c",
    "--check",
    help="Only check if formatting is correct, do not update.",
    action="store_true",
)
args = parser.parse_args()

if args.reformat is not None:
    reformat_files(*args.reformat, check=args.check)


log.logger.dotted = not args.no_dotted

configs = [f for f in os.listdir(os.curdir) if f.endswith(".ok")]

if args.files is not None:
    file_names = [os.path.basename(file.name) for file in args.files]
    for file in args.files:
        file.close()
else:
    file_names = []
    if len(configs) > 1:
        parser.error(
            "Multiple okpy configs detected, files to be tested must be specified explicitly."
        )
    elif len(configs) > 0:
        with open(configs[0]) as f:
            file_names = [
                name for name in json.loads(f.read())["src"] if name.endswith(".scm")
            ]
local_server.start(file_names, args.port, not args.nobrowser)
