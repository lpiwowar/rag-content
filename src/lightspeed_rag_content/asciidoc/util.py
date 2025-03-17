# Copyright 2025 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import argparse


def get_common_arg_parser() -> argparse.ArgumentParser:
    """Get default argument parser for asciidoc related operations."""
    parser = argparse.ArgumentParser(
        description="Command that can be used to convert asciidoc format to txt format.")

    parser.add_argument(
        "-i"
        "--input-file",
        required=True,
        type=str,
        help="A file in asciidoc format that should be converted to text."
    )

    parser.add_argument(
        "-o",
        "--output-file",
        required=True,
        type=str,
        help="File where the file in the text format should be stored."
    )

    parser.add_argument(
        "-a",
        "--atributes-file",
        required=False,
        type=str,
        help="File containing attributes that should be passed to asciidoctor."
    )

    parser.add_argument(
        "-c",
        "--converter-file",
        required=False,
        type=str,
        help="Ruby code that should be used to convert the file."
    )

    return parser
