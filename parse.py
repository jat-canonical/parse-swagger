#!/usr/bin/env python

import argparse
import json

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

AMS_CONFIG_PATH = "/1.0/config"


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="AMS swagger parser",
        description="Extracts AMS configuration data",
    )
    parser.add_argument(
        "swagger_path",
        help="Source for the configuration file (Should conform to swagger spec 2.0)",
    )
    parser.add_argument(
        "--output",
        dest="output_file",
        help="Source for the configuration file (Should conform to swagger spec 2.0)",
        default="ams-configuration.md",
    )
    args = parser.parse_args()
    with open(args.swagger_path, mode="r") as f:
        swagger = json.load(f)
    config_props = swagger["paths"][AMS_CONFIG_PATH]["get"]["responses"]["200"][
        "schema"
    ]["properties"]["metadata"]["properties"]["config"]["properties"]
    node_props = swagger["definitions"]["NodePatch"]["properties"]
    env = Environment(loader=FileSystemLoader("."))
    templ = env.get_template("template.md.j2")
    text = templ.render(configs=config_props, nodes=node_props)
    with open(args.output_file, mode="w+") as op:
        op.write(text)


if __name__ == "__main__":
    SystemExit(main())
