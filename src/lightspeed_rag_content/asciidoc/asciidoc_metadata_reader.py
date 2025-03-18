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
import sys
from importlib import resources
from pathlib import Path

LOG = logging.getLogger(__package__)
logging.basicConfig(level=logging.INFO)

def main(argv: list):
    package_dir: Path = resources.files(__package__)
    dumper_script_path: Path = package_dir / "ruby_asciidoc" / "asciidoc_structure_dumper.rb"

    ruby_cmd = shutil.which("ruby")
    if not ruby_cmd:
        LOG.error("Missing ruby executable")
        sys.exit(1)

    try:
        subprocess.run([  # noqa: S603
            ruby_cmd,
            str(dumper_script_path.absolute()),
            argv[1]
        ], check=True, shell=False)
    except subprocess.CalledProcessError as e:
        LOG.error(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
