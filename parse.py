#!/usr/bin/env python3

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

    configs = _parse_config_schema(swagger)
    nodes = _parse_node_schema(swagger)
    env = Environment(loader=FileSystemLoader("."))
    templ = env.get_template("template.md.j2")
    text = templ.render(configs=configs, nodes=nodes)
    with open(args.output_file, mode="w+") as op:
        op.write(text)


def _parse_config_schema(swagger) -> dict:
    config_props = swagger["paths"][AMS_CONFIG_PATH]["get"]["responses"]["200"][
        "schema"
    ]["properties"]["metadata"]["properties"]["config"]["properties"]
    for prop in config_props.values():
        if "description" in prop:
            prop["description"] = prop["description"].replace("\n", " ")
    return config_props


def _parse_node_schema(swagger) -> dict:
    node_props = swagger["definitions"]["NodePatch"]["properties"]
    for base, prop in dict(node_props).items():
        key = ""
        if prop["type"] == "object":
            key = "additionalProperties"
        if prop["type"] == "array":
            key = "items"
        if key:
            if schema_name := prop[key].get("$ref"):
                name = schema_name.split("/")[-1]
                if schema := swagger["definitions"][name]:
                    for subprop_name, subprop_attrs in schema["properties"].items():
                        if subprop_name == "id":
                            continue
                        new_base = base
                        if base == "gpus":
                            new_base = f"{base}.<id>"
                        node_props[f"{new_base}.{subprop_name}"] = subprop_attrs
            node_props.pop(base)
        else:
            val = node_props.pop(base)
            node_props[base.replace("_", "-")] = val
        if "description" in prop:
            prop["description"] = prop["description"].replace("\n", " ")
        return node_props


if __name__ == "__main__":
    SystemExit(main())
