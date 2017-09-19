#!/usr/bin/env python3

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
from flask import Flask
from maat import MaatAgent, create_agent_api


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Maât-Agent")
    parser.add_argument(
        "--process_name", default="rsession", type=str,
        help="The name of the process to watch"
    )
    parser.add_argument("-s", "--sleep_time", default=5.0, type=float, help="Interval between each refresh of data")
    parser.add_argument(
        "--process_interval", default=2.5, type=float,
        help="Time between refresh process"
    )
    parser.add_argument("-o", "--host", default="0.0.0.0", type=str, help="Host to listen to")
    parser.add_argument("-p", "--port", default=5000, type=int, help="Port to listen to")

    args = parser.parse_args()

    maat_agent = MaatAgent(
        args.process_name, sleep_time=args.sleep_time, process_interval=args.process_interval
    )

    app = Flask("Maat-Agent")

    create_agent_api(args.host, args.port, maat_agent, app)