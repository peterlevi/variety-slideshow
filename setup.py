#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (c) 2015, Peter Levi <peterlevi@peterlevi.com>
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

###################### DO NOT TOUCH THIS (HEAD TO THE SECOND PART) ######################

import sys

try:
    import DistUtilsExtra.auto
    from DistUtilsExtra.command.build_icons import build_icons
except ImportError:
    print(
        "To build variety-slideshow you need python3-distutils-extra - "
        "https://launchpad.net/python-distutils-extra",
        file=sys.stderr,
    )
    sys.exit(1)
assert DistUtilsExtra.auto.__version__ >= "2.18", "needs DistUtilsExtra.auto >= 2.18"


class InstallAndUpdateDataDirectory(DistUtilsExtra.auto.install_auto):
    def run(self):
        DistUtilsExtra.auto.install_auto.run(self)


DistUtilsExtra.auto.setup(
    name="variety-slideshow",
    version="0.1",
    license="GPL-3",
    author="Peter Levi",
    author_email="peterlevi@peterlevi.com",
    description="Variety Slideshow",
    long_description='A pan-and-zoom image slideshow. Run "variety-slideshow --help" to see options.',
    url="https://github.com/peterlevi/variety-slideshow",
    cmdclass={"install": InstallAndUpdateDataDirectory, "build_icons": build_icons},
)
