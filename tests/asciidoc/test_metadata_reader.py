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

import importlib.resources
import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch
import importlib
import subprocess

from lightspeed_rag_content.asciidoc.asciidoc_metadata_reader import main
from lightspeed_rag_content.asciidoc import AsciidocConverter


class TestMetadataReader(unittest.TestCase):
    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.subprocess.run')
    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test_main(self, mock_which, mock_run):
        # mock_which.return_value = "/usr/bin/ruby"
        # main(["command", "input.adoc"])
        # mock_run.assert_called_with([
        #     "/usr/bin/ruby",
        #     str(Path(importlib.resources.files(main.__module__)).absolute()),
        #     "input.adoc"
        # ], check=True, capture_output=True)
        # TODO fixme
        pass

    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.subprocess.run')
    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test_main_incorrect_asciidoctor_cmd(self, mock_which, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(cmd="asciidoctor", returncode=1)

        with self.assertRaises(SystemExit) as e:
            main(["command", "input.adoc"])
            self.assertEqual(e.exception.code, 1)

    @patch('lightspeed_rag_content.asciidoc.asciidoc_converter.shutil.which')
    def test_main_missing_asciidoctor_cmd(self, mock_which):
        mock_which.return_value = ""

        with self.assertRaises(SystemExit) as e:
            with self.assertLogs() as logger:
                main(["command", "input.adoc"])
                self.assertEqual(e.exception.code, 1)

                error_msgs = [ output for output in logger.output if "ERROR" in output]
                self.assertTrue(len(error_msgs) > 0)

