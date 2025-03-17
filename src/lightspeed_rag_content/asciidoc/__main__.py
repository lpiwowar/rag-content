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

from lightspeed_rag_content.asciidoc.asciidoc_converter import AsciidocConverter
from lightspeed_rag_content.asciidoc.util import get_common_arg_parser

if __name__ == "__main__":
    parser = get_common_arg_parser()
    args = parser.parse_args()

    converter = AsciidocConverter(args.attributes_file, args.converter_file)
    converter.asciidoc_to_txt_file(args.input_file, args.output_file)