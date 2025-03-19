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

"""This module contains AsciidocConverter that can be used to convert asciidoc files.

The code in this module is heavily dependent on ruby and asciidoctor. These commands have
to be installed prior to the usage of this module. Otherwise monsters and dragons are
waiting for you!

Typical usage example:

    >>> adoc_converter = AsciidocConverter()
    >>> adoc_converter.convert(Path("input.adoc"), Path("output.txt"))

An example of of more involved usage:

    >>> adoc_converter = AsciidocConverter(
    ...    target_format='custom_format',
    ...    attributes_file='./attributes.yaml',
    ...    converter_file='./asciidoc_custom_format_converter.rb'
    ... )
    >>> adoc_converter.convert(Path("input.adoc"), Path("output.txt"))

'attributes.yaml' content:

    ---
    attribute_name_1: attribute_value_1
    attribute_name_2: attribute_value_2
    ...

The 'asciidoc_custom_format_converter.rb' has to be compatible with asciidoctor.
Please read: https://docs.asciidoctor.org/asciidoctor/latest/extensions/
You can also investigate the default text converter 'asciidoc_text_converter.rb'
stored in the asciidoc package.
"""

import logging
import shutil
import subprocess
from importlib import resources
from pathlib import Path

import yaml

LOG: logging.Logger = logging.getLogger(__name__)

RUBY_ASCIIDOC_DIR: Path = resources.files(__package__).joinpath("ruby_asciidoc")

class AsciidocConverter:
    """Convert asciidoc formated documents to different formats.

    The class requires asciidoctor to be installed. By default all files are
    converted to text format using a custom library (written in ruby) compatible
    with asciidoctor.

    Attributes:
        asciidoctor_cmd: A path pointing to asciidoctor executable.
        target_format: A format to which input files should be converted.
        attributes_file: A path pointing to attributes file.
        converter_file:
            A ruby script that should be used to convert input files to
            target_format.

    """

    def __init__(self, target_format: str = "text", attributes_file: Path | None = None,
                 converter_file: Path | None = None):
        """Initializes AsciidocConverter.

        Args:
            target_format: A format to which input files should be converted.
            attributes_file: A path pointing to attributes file.
            converter_file:
                A ruby script that should be used to convert input files to
                target_format.

        Raises:
            FileNotFoundError:
                When asciidoctor executable or converter_file can not be found.
        """
        self.target_format = target_format
        self.attribute_list = self._get_attribute_list(attributes_file)

        if converter_file:
            self.converter_file = converter_file
        else:
            self.converter_file = self._get_default_converter_file(target_format)

        self.asciidoctor_cmd = self._get_asciidoctor_path()

    @staticmethod
    def _get_default_converter_file(target_format: str) -> None:
        """Returns path to ruby script that supports """
        converter_files = {
            "text": "asciidoc_text_converter.rb",
        }

        library_file = converter_files.get(target_format, None)
        if not library_file:
            raise FileNotFoundError("Target format {target_format} does not have default library file.")

        return RUBY_ASCIIDOC_DIR.joinpath(library_file)

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
        """Convert file containing attributes to list of -a <key>=<value> pairs."""
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
            source_file: A path of a file that should be converted.
            destination_file: A path of where the converted file should be stored.

        Raises:
            subprocess.CalledSubprocessError:
                If an error occurss when running asciidoctor.
        """
        LOG.info("Processing: " + str(source_file.absolute()))
        if destination_file.exists():
            LOG.warning(f"Destination file {destination_file} exists. It will be overwritten!")
        else:
            destination_file.mkdir(parents = True, exist_ok=True)

        command = [self.asciidoctor_cmd]

        if self.attribute_list:
            command += self.attribute_list
        if self.converter_file:
            command += ["-r", str(self.converter_file.absolute())]

        command = [
            *command,
            "-b",
            self.target_format,
            "-o",
            str(destination_file.absolute()),
            "--trace",
            "--quiet",
            str(source_file.absolute()),
        ]

        subprocess.run(command, check=True, capture_output=True)  # noqa: S603

