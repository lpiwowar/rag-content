#!/usr/bin/env python3

"""Utility script to convert OCP docs from adoc to plain text."""

import argparse
import logging
import os

import yaml

from lightspeed_rag_content.asciidoc.asciidoc_converter import AsciidocConverter

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def node_in_distro(node: dict, distro: str) -> bool:
    """Check if a node is in a distro."""
    return node.get("Distros", "") == "" or distro in node.get("Distros", "").split(",")

def process_node(node: dict, distro: str, dir: str = "", file_list: list = []) -> list:
    """Process YAML node from the topic map."""
    currentdir = dir

    if node_in_distro(node, distro) and "Topics" in node:
        currentdir = os.path.join(currentdir, node["Dir"])
        for subnode in node["Topics"]:
            file_list = process_node(
                subnode, distro, dir=currentdir, file_list=file_list
            )
    elif node_in_distro(node, distro):
        file_list.append(os.path.join(currentdir, node["File"]))

    return file_list

def get_file_list() -> list:
    """Get list of ALL documentation files that should be processed."""
    topic_map = os.path.normpath(os.path.join(os.getcwd(), args.topic_map))
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
        description="This command converts asciidoc documentation to txt format.",
        usage="TODO [options]",
    )

    parser.add_argument(
        "-i",
        "--input-dir",
        required=True,
        type=str,
        help="The input directory containing asciidoc formated documentation",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        required=True,
        type=str,
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
        type=str,
        help="The topic map file",
    )

    return parser


if __name__ == "__main__":
    parser = get_arg_parser()
    args = parser.parse_args()

    input_dir = os.path.normpath(args.input_dir)
    output_dir = os.path.normpath(args.output_dir)
    file_list = get_file_list()
    os.makedirs(output_dir, exist_ok=True)

    converter = AsciidocConverter(attributes_file=args.attributes)

    for filename in file_list:
        input_file = os.path.join(input_dir, filename + ".adoc")
        output_file = os.path.join(output_dir, filename + ".txt")

        os.makedirs(os.path.dirname(os.path.realpath(output_file)), exist_ok=True)
        converter.asciidoc_to_txt_file(input_file, output_file)
