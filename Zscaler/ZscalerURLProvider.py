#!/usr/local/autopkg/python
#
# Copyright 2023 Rick Heil
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# pylint: disable=C0103
"""See docstring for ZscalerURLProvider class"""

import json
import re
from distutils.version import LooseVersion
import sys
sys.path.insert(0, "/Library/AutoPkg")
from autopkglib.URLGetter import URLGetter

__all__ = ["ZscalerURLProvider"]

# This provider scrapes versions for download from the release notes
# published on the Zscaler help CMS.
# pylint: disable=C0301
NOTES_DATA_URL = "https://help.zscaler.com/zapi/fetch-data?url_alias=/client-connector/client-connector-app-release-summary-2023&view_type=full&cloud=www.google.com&domain=zscaler&applicable_category=2896&applicable_version=all&applicable_parent_version=&keyword=undefined&language=en&_format=json"
# pylint: enable=C0301

INCLUDE_LIMITED = False
CLOUDFRONT_DISTRO = "https://d32a6ru7mhaq0c.cloudfront.net"

class ZscalerURLProvider(URLGetter):
    """Provides URL to the latest Zscaler client release."""

    description = __doc__
    input_variables = {
        "include_limited": {
            "required": False,
            "description": (
                f"Include limited availability releases. Defaults to '{INCLUDE_LIMITED}'."
            ),
        },
        "notes_data_url": {
            "required": False,
            "description": (
                f"URL to the JSON of current release notes page. Defaults to '{NOTES_DATA_URL}'."
            ),
        },
        "cloudfront_distro_url": {
            "required": False,
            "description": (
                f"URL for Zscaler Cloudfront distribution point. Defaults to '{CLOUDFRONT_DISTRO}'."

            ),
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest Zscaler release."
        },
        "filename": {
            "description": "The Zscaler provided filename to save the download as."
        },
        "version": {
            "description": "Version of the latest Zscaler release."
        },
    }

    def get_zscaler_version(self, notes_data_url, include_limited):
        """Returns the latest version number by scraping release notes."""
        self.output(f"Using default notes_data_url of {notes_data_url}", 3)
        json_response = self.download(notes_data_url)
        zscaler_info = json.loads(json_response)
        self.output(zscaler_info, 4)
        versions = []
        for entry in zscaler_info["data"]["body"]["release_notes"]["entries"]:
            entry_data = zscaler_info["data"]["body"]["release_notes"]["entries"][entry]
            if "limited" in entry_data["release"]:
                extracted = re.search(r"Client\ Connector\ ([\d\.]*)\ for macOS",
                                      entry_data["release"]["limited"][0]["title"]).group(1)
                if len(extracted) > 0 and include_limited:
                    self.output(f"Found limited release {extracted} - adding to list.", 3)
                    versions.append(extracted)
            else:
                extracted = re.search(r"Client\ Connector\ ([\d\.]*)\ for macOS",
                                      entry_data["release"]["available"][0]["title"]).group(1)
                if len(extracted) > 0:
                    self.output(f"Found GA release {extracted} - adding to list.", 3)
                    versions.append(extracted)

        # compare all extracted versions to find highest
        newest_version = None
        for version in versions:
            self.output(f"Processing found version {version}")
            if newest_version is None or LooseVersion(version) > LooseVersion(newest_version):
                newest_version = version
        self.output(f"Found newest version of Zscaler Client Connector as {newest_version}.")
        return newest_version

    def main(self):
        """Main function"""
        include_limited = self.env.get("include_limited", INCLUDE_LIMITED)
        if include_limited != INCLUDE_LIMITED:
            self.output(f"INCLUDE_LIMITED overridden to {include_limited}", 3)
        notes_data_url = self.env.get("notes_data_url", NOTES_DATA_URL)
        if notes_data_url != NOTES_DATA_URL:
            self.output(f"NOTES_DATA_URL overridden to {notes_data_url}", 3)

        # get latest version number
        version = self.get_zscaler_version(notes_data_url, include_limited)

        # assemble output
        self.env["url"] = f"{CLOUDFRONT_DISTRO}/Zscaler-osx-{version}-installer.app.zip"
        self.env["filename"] = f"Zscaler-osx-{version}-installer.app.zip"
        self.env["version"] = version


if __name__ == "__main__":
    run = ZscalerURLProvider()
    run.main()
    print(f'Found URL:      {run.env.get("url")}')
    print(f'Found filename: {run.env.get("filename")}')
    print(f'Found version:  {run.env.get("version")}')
