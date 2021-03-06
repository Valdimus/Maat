#!/usr/bin/env python3

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

from gevent import monkey
monkey.patch_all(thread=False)

import logging
import argparse
from flask import Flask
from maat import LoadBalancer, BackendManager, Backend, Resource, HTTPAgentResource
from maat_webservice import TestWebservice

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":


    parser = argparse.ArgumentParser(description="Maât")
    parser.add_argument("-i", "--interval", default=60, type=int, help="Interval between each refresh of data")
    parser.add_argument("-o", "--host", default="0.0.0.0", type=str, help="Host to listen to")
    parser.add_argument("-p", "--port", default=5000, type=int, help="Port to listen to")
    parser.add_argument("-m", "--max_session", default=1, type=int, help="Maximum number session vy user")


    args = parser.parse_args()

    local_test = False

    b1, b2, b3 = None, None, None
    if local_test:
        pass
        # b1 = Backend(
        #     name="b1",
        #     service=Resource()
        #     hostname="127.0.0.1", port=5001, agent_port=5001,
        #     monitoring_interval=0, sessions_interval=0, ping_interval=0, timeout=0.1
        # )
        # b2 = Backend(
        #     name="b2",
        #     hostname="127.0.0.1", port=5002, agent_port=5002,
        #     monitoring_interval=0, sessions_interval=0, ping_interval=0, timeout=0.1
        # )
        # b3 = Backend(
        #     name="b3",
        #     hostname="127.0.0.1", port=5003, agent_port=5003,
        #     monitoring_interval=0, sessions_interval=0, ping_interval=0, timeout=0.1
        # )
    else:
        b1 = Backend(
            name="machine1",
            service=Resource("192.168.5.24", 8787, name="service-machine1"),
            agent=HTTPAgentResource("192.168.5.24", 5000)
        )
        b2 = Backend(
            name="machine2",
            service=Resource("192.168.5.28", 8787, name="service-machine2"),
            agent=HTTPAgentResource("192.168.5.28", 5000)
        )
        b3 = Backend(
            name="machine3",
            service=Resource("192.168.5.46", 8787, name="service-machine3"),
            agent=HTTPAgentResource("192.168.5.46", 5000)
        )

    backend_manager = BackendManager(backends=[b1, b2, b3])
    laod_balancer = LoadBalancer(backend_manager, max_sessions_by_user=args.max_session)
    app = Flask("Maât")
    app.secret_key = 'Aj/TaX/,0ZyX ]LW?!jmRR~X3HH3Nr98'
    wb = TestWebservice(laod_balancer, app=app)

    wb.run(host=args.host, port=args.port)
