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
import shutil
import subprocess
from importlib import resources
from pathlib import Path

import yaml

LOG = logging.getLogger(__name__)


class AsciidocConverter:
    """Convert asciidoc formated documents to different formats.

    The class requires ruby to be installed on the local machine as well as the
    asciidoctor tool. If the tools are not present Exception is raised.

    Raises:
        FileNotFoundError: When asciidoctor executable can not be found.
    """

    LIBRARY_FILE: Path = resources.files(__package__).joinpath("ruby_asciidoc/asciidoc_text_converter.rb")

    def __init__(self, target_format: str = "text", attributes_file: Path | None = None,
                 library_file: Path = LIBRARY_FILE):
        """AsciidocConverter constructor.

        Args:
            attributes_file: Absolute path pointing to the attributes file.
            library_file: File containing the logic to convert the file.
            target_format: What is the target format.
        """
        self.asciidoctor_cmd = self._get_asciidoctor_path()

        self.attribute_list = self._get_attribute_list(attributes_file)
        self.library_file = library_file
        self.target_format = target_format

    @staticmethod
    def _get_asciidoctor_path() -> str:
        """Check whether asciidoctor and ruby is installed."""
        asciidoctor_path = shutil.which("asciidoctor")
        if not asciidoctor_path:
            raise FileNotFoundError("asciidoctor executable not found")

        LOG.info(f"Using asciidoctor with {asciidoctor_path} path")
        return asciidoctor_path

    @staticmethod
    def _get_attribute_list(attributes_file: Path) -> list:
        """Convert file containing attributes to list of <key>=<value> pairs."""
        attribute_list: list = []

        if attributes_file is None:
            return attribute_list

        with open(attributes_file, "r") as file:
            attributes = yaml.safe_load(file)

            if attributes is None:
                return attribute_list

            for key, value in attributes.items():
                attribute_list += ["-a", key + "=%s" % value]

        return attribute_list


    def convert(self, source_file: Path, destination_file: Path) -> None:
        """Convert asciidoc file to target format.

        Args:
            source_file: Filepath of a file that should be converted.
            destination_file: Filepath of a destination where the converted file should be stored.

        Raises:
            subprocess.CalledSubprocessError: If an error occurss when running asciidoctor.
        """
        LOG.info("Processing: " + str(source_file.absolute()))
        if destination_file.exists():
            LOG.warning(f"Destination file {destination_file} exists. It will be overwritten.")

        command = [self.asciidoctor_cmd]
        command = command + self.attribute_list
        command = [
            *command,
            "-r",
            str(self.library_file.absolute()),
            "-b",
            self.target_format,
            "-o",
            str(destination_file.absolute()),
            "--trace",
            "--quiet",
            str(source_file.absolute()),
        ]

        subprocess.run(command, check=True, capture_output=True)  # noqa: S603

