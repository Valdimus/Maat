# coding: utf-8

# Copyright (C) 2017 NOUCHET Christophe
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

# Author: Christophe Nouchet
# Email: nouchet.christophe@gmail.com
# Date: 23/03/2017

import argparse
from tests import create_fake_pls_backend


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Maât agent")
    parser.add_argument("-i", "--interval", default=60, type=int, help="Interval between each refresh of data")
    parser.add_argument("-o", "--host", default="0.0.0.0", type=str, help="Host to listen to")
    parser.add_argument("-p", "--port", default=5005, type=int, help="Port to listen to")

    args = parser.parse_args()

    create_fake_pls_backend(host=args.host, port=args.port, interval=args.interval)