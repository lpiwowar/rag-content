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
import os
import subprocess
from importlib import resources

import yaml

LOG = logging.getLogger(__name__)
# TODO resolve logging. Do I want to use INFO level?
logging.basicConfig(level=logging.INFO)


class AsciidocConverter:
    """Converts asciidoc formated documents to different formats.

    The class requires ruby to be installed on the local machine as well as the
    asciidoc tool. If the tools are not present Exception is raised.
    """

    CONVERTER_FILE: str = "asciidoc_text_converter.rb"

    def __init__(self, attributes_file: str = "", converter_file: str = CONVERTER_FILE,
                 backend: str = "text"):
        """AsciidocConverter constructor.

        Args:
            attributes_file: str: Absolute path pointing to the attributes file.
            converter_file: str: File containing the logic to convert the file.
            backend: str: What is the target format.
        """
        self._check_asciidoctor_available()

        self.attribute_list = self._get_attribute_list(attributes_file)
        self.converter_file = str(resources.files(__package__).joinpath(converter_file))
        self.backend = backend

    @staticmethod
    def _check_asciidoctor_available():
        """Check whether asciidoctor and ruby is installed"""
        # TODO use subprocess.run safely
        # TODO use shutils.which
        result = subprocess.run(["/usr/bin/asciidoctor", "--version"],
                                check=True, capture_output=True)
        if result.returncode != 0:
            # TODO raise appropriate exception
            raise Exception("asciidoctor command not found")
        else:
            LOG.debug(f"Using asciidoctor version: {result.stdout}")

        # TODO use subprocess.run safely
        result = subprocess.run(["/usr/bin/ruby", "--version"], check=True, capture_output=True)
        if result.returncode != 0:
            raise Exception("asciidoctor command not found")
        else:
            LOG.debug(f"Using ruby version: {result.stdout}")

    @staticmethod
    def _get_attribute_list(attributes_file: str) -> list:
        """Convert file containing attributes to list of <key>=<value> pairs."""
        attribute_list: list = []

        if attributes_file is None:
            return attribute_list

        with open(attributes_file, "r") as file:
            attributes = yaml.safe_load(file)

            for key, value in attributes.items():
                attribute_list = [*attribute_list, "-a", key + "=%s" % value]

        return attribute_list


    def asciidoc_to_txt_file(self, asciidoc_filepath: str, txt_filepath: str) -> None:
        """Convert .adoc file to .txt.

        Args:
            asciidoc_filepath: str: Absolute path pointing to the asciidoc file
            txt_filepath: str: Path where the converted file should be stored

        Raises:
            Exception: When the source asciidoc file does not exist.
        """
        LOG.info("Processing: " + asciidoc_filepath)

        if not os.path.isfile(asciidoc_filepath):
            raise Exception("The asciidoc file does not exist.")

        if os.path.isFile(txt_filepath):
            LOG.warning(f"Destination file {txt_filepath} exists. Overwriting.")

        command = ["asciidoctor"]
        command = command + self.attribute_list
        command = [
            *command,
            "-r",
            self.converter_file,
            "-b",
            self.backend,
            "-o",
            txt_filepath,
            "--trace",
            "--quiet",
            asciidoc_filepath,
        ]

        # TODO use subprocess.run safely
        result = subprocess.run(command, check=True, capture_output=True)
        if result.returncode != 0:
            LOG.error(result.stderr)
            LOG.error(result.stdout)

        return

