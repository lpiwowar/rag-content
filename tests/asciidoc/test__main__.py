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
import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch
import subprocess

from lightspeed_rag_content.asciidoc import RUBY_ASCIIDOC_DIR
from lightspeed_rag_content.asciidoc.__main__ import (
    main_convert,
    main_get_structure,
    get_argument_parser,
)

class Test__main__(unittest.TestCase):

    def get_mock_parsed_args(self) -> Mock:
        mock_args = Mock()
        mock_args.input_file = Path("input.adoc")
        mock_args.output_file = Path("output.txt")
        mock_args.attributes_file = None
        mock_args.target_format = "text"

        return mock_args

    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.subprocess.run')
    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test_main_convert(self, mock_which, mock_run):
        mock_which.return_value = "/usr/bin/asciidoctor"
        mock_args = self.get_mock_parsed_args()
        main_convert(mock_args)

        mock_run.assert_called_with([
            "/usr/bin/asciidoctor",
            "-r",
            str(RUBY_ASCIIDOC_DIR.joinpath("asciidoc_text_converter.rb")),
            "-b",
            "text",
            "-o",
            str(Path("output.txt").absolute()),
            "--trace",
            "--quiet",
            str(Path("input.adoc").absolute()),
        ], check=True, capture_output=True)

    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.subprocess.run')
    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test_main_convert_incorrect_cmd_error(self, mock_which, mock_run):
        mock_which.return_value = "/usr/bin/asciidoctor"
        mock_run.side_effect = subprocess.CalledProcessError(cmd="asciidoctor", returncode=1)
        mock_args = self.get_mock_parsed_args()

        with self.assertRaises(SystemExit) as e:
            main_convert(mock_args)
            self.assertNotEqual(e.exception.code, 0)

    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test_main_convert_missing_asciidoctor_cmd(self, mock_which):
        mock_which.return_value = ""
        mock_args = self.get_mock_parsed_args()

        with self.assertRaises(SystemExit) as e:
            main_convert(mock_args)
            self.assertNotEqual(e.exception.code, 0)

    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.subprocess.run')
    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test_main_get_structure(self, mock_which, mock_run):
        mock_which.return_value = "/usr/bin/ruby"
        mock_args = Mock()
        mock_args.input_file = Path("input.adoc")

        main_get_structure(mock_args)
        mock_run.assert_called_with([
            "/usr/bin/ruby",
            str(RUBY_ASCIIDOC_DIR.joinpath("asciidoc_structure_dumper.rb")),
            str(Path("input.adoc").absolute()),
        ], check=True, capture_output=True)

    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.subprocess.run')
    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test_main_incorrect_asciidoctor_cmd(self, mock_which, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(cmd="asciidoctor", returncode=1)
        mock_args = Mock()
        mock_args.input_file = Path("input.adoc")

        with self.assertRaises(SystemExit) as e:
            main_get_structure(mock_args)
            self.assertNotEqual(e.exception.code, 0)

    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test_main_missing_asciidoctor_cmd(self, mock_which):
        mock_which.return_value = ""
        mock_args = Mock()
        mock_args.input_file = Path("input.adoc")

        with self.assertRaises(SystemExit) as e:
            with self.assertLogs() as logger:
                main_get_structure(mock_args)
                self.assertNotEqual(e.exception.code, 0)

                error_msgs = [ output for output in logger.output if "ERROR" in output]
                self.assertTrue(len(error_msgs) > 0)

    def test_get_argument_parser(self):
        args = get_argument_parser()

        self.assertIsInstance(args, argparse.ArgumentParser)

