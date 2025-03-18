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

import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch
import subprocess

import yaml

from lightspeed_rag_content.asciidoc import AsciidocConverter
from lightspeed_rag_content.asciidoc.__main__ import main

class TestAsciidocConverter(unittest.TestCase):

    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.subprocess.run')
    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test_convert(self, mock_which, mock_run):
        mock_which.return_value = "/usr/bin/asciidoctor"
        adoc_text_converter = AsciidocConverter(target_format="text", attributes_file=None)
        adoc_text_converter.convert(Path("input.adoc"), Path("output.txt"))

        mock_run.assert_called_with([
            "/usr/bin/asciidoctor",
            "-r",
            str(AsciidocConverter.LIBRARY_FILE),
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
    def test_convert_overwrite_output_file(self, mock_which, mock_run):
        mock_which.return_value = "/usr/bin/asciidoctor"
        adoc_text_converter = AsciidocConverter(target_format="text", attributes_file=None)

        mock_output_file = Mock()
        mock_output_file.exists.return_value = True

        with self.assertLogs() as logger:
            adoc_text_converter.convert(Path("input.adoc"), mock_output_file)
            warning_msgs = [ output for output in logger.output if "WARNING" in output ]
            self.assertTrue(len(warning_msgs) > 0)

    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test__get_asciidoctor_path(self, mock_which):
        mock_which.return_value = ""
        with self.assertRaises(FileNotFoundError):
            AsciidocConverter(target_format="text", attributes_file=None)

    def test__get_attributes_list_valid_yaml(self):
        test_attributes_file="""---
        foo: bar
        """

        with patch('builtins.open', mock_open(read_data=test_attributes_file)) as m:
            AsciidocConverter._get_attribute_list("foo_bar.yaml")
            m.assert_called_once()

    def test__get_attributes_list_invalid_yaml(self):
        test_attributes_file="""---
        [[]
        """

        with patch('builtins.open', mock_open(read_data=test_attributes_file)):
            with self.assertRaises(yaml.parser.ParserError):
                AsciidocConverter._get_attribute_list("foo_bar.yaml")

    def test__get_attributes_list_empty_yaml(self):
        with patch('builtins.open', mock_open(read_data="")):
            attributes = AsciidocConverter._get_attribute_list("foo_bar.yaml")
            self.assertEqual(attributes, [])

    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.subprocess.run')
    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test_main(self, mock_which, mock_run):
        mock_which.return_value = "/usr/bin/asciidoctor"
        main(["-i", "input.adoc", "-o", "output.txt"])

        mock_run.assert_called_with([
            "/usr/bin/asciidoctor",
            "-r",
            str(AsciidocConverter.LIBRARY_FILE),
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
    def test_main_incorrect_asciidoctor_cmd(self, mock_which, mock_run):
        mock_which.return_value = "/usr/bin/asciidoctor"
        mock_run.side_effect = subprocess.CalledProcessError(cmd="asciidoctor", returncode=1)

        with self.assertRaises(SystemExit) as e:
            main(["-i", "input.adoc", "-o", "output.txt"])
            self.assertEqual(e.exception.code, 1)

    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test_main_missing_asciidoctor_cmd(self, mock_which):
        mock_which.return_value = ""

        with self.assertRaises(SystemExit) as e:
            main(["-i", "input.adoc", "-o", "output.txt"])
            self.assertEqual(e.exception.code, 1)


