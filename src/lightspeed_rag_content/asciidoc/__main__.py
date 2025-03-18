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
import logging
import subprocess
import sys
from pathlib import Path

from lightspeed_rag_content.asciidoc.asciidoc_converter import AsciidocConverter
from lightspeed_rag_content.asciidoc.utils import get_common_arg_parser

LOG = logging.getLogger(__package__)
logging.basicConfig(level=logging.INFO)

def main(argv):
    parser = get_common_arg_parser()
    parser.prog = "lightspeed_rag_content.asciidoc"

    parser.add_argument(
        "--input-file",
        "-i",
        required=True,
        type=Path,
        help="A file in asciidoc format that should be converted to text."
    )

    parser.add_argument(
        "--output-file",
        "-o",
        required=True,
        type=Path,
        help="File where the file in the text format should be stored."
    )

    args = parser.parse_args(argv)

    try:
        converter = AsciidocConverter(target_format="text", attributes_file=args.attributes_file)
        converter.convert(args.input_file, args.output_file)
    except subprocess.CalledProcessError as e:
        LOG.error(e.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError as e:
        LOG.error(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
