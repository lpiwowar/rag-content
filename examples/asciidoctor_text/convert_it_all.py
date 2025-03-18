#!/usr/bin/env python3

"""Utility script to convert OCP docs from adoc to plain text."""

import argparse
import logging
from pathlib import Path

import yaml

from lightspeed_rag_content.asciidoc.asciidoc_converter import AsciidocConverter

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def node_in_distro(node: dict, distro: str) -> bool:
    """Check if a node is in a distro."""
    return node.get("Distros", "") == "" or distro in node.get("Distros", "").split(",")

def process_node(node: dict, distro: str, dir: Path = Path(),
                 file_list: list[Path] = []) -> list:
    """Process YAML node from the topic map."""
    currentdir = dir

    if not node_in_distro(node, distro):
        return file_list

    if "Topics" in node:
        currentdir = currentdir.joinpath(node["Dir"])
        for subnode in node["Topics"]:
            file_list = process_node(
                subnode, distro, dir=currentdir, file_list=file_list
            )
    else:
        file_list.append(currentdir.joinpath(node["File"]))

    return file_list

def get_file_list(topic_map: Path) -> list:
    """Get list of ALL documentation files that should be processed."""
    topic_map = Path().joinpath(args.topic_map).absolute()
    with open(topic_map, "r") as fin:
        topic_map = yaml.safe_load_all(fin)
        mega_file_list: list = []
        for map in topic_map:
            file_list: list = []
            file_list = process_node(map, args.distro, file_list=file_list)
            mega_file_list = mega_file_list + file_list

    return mega_file_list

def get_arg_parser() -> argparse.ArgumentParser:
    """Get argument parser for the OpenShift asciidoc command."""
    parser = argparse.ArgumentParser(
        description="This command converts asciidoc documentation to txt format."
    )

    parser.add_argument(
        "-i",
        "--input-dir",
        required=True,
        type=Path,
        help="The input directory containing asciidoc formated documentation",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        required=True,
        type=Path,
        help="The output directory for text",
    )

    parser.add_argument(
        "-a",
        "--attributes",
        required=False,
        type=str,
        help="An optional file containing attributes"
    )

    parser.add_argument(
        "-d",
        "--distro",
        required=True,
        type=str,
        help="OpenShift distro the docs are for, ex. openshift-enterprise",
    )

    parser.add_argument(
        "-t",
        "--topic-map",
        required=True,
        type=Path,
        help="The topic map file",
    )

    parser.add_argument(
        "-c",
        "--converter-file",
        required=False,
        type=Path,
        help="Ruby code that should be used to convert the file."
    )

    return parser


if __name__ == "__main__":
    parser = get_arg_parser()
    args = parser.parse_args()
    file_list = get_file_list(args.topic_map)

    input_dir = args.input_dir.absolute()
    output_dir = args.output_dir.absolute()

    output_dir.mkdir(parents=True, exist_ok=True)

    adoc_text_converter = AsciidocConverter(target_format="text", attributes_file=args.attributes)

    for filename in file_list:
        input_file = input_dir.joinpath(filename.with_suffix(".adoc"))
        output_file = output_dir.joinpath(filename.with_suffix(".txt"))

        output_file.absolute().parent.mkdir(parents=True, exist_ok=True)
        adoc_text_converter.convert(input_file, output_file)
