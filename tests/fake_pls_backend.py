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

import time
import json
import argparse
from flask import Flask, redirect, request
from threading import Lock

from maat import Monitoring


class FakePLSBackend:
    """An esay way to test the laod balance function without the real backend"""

    def __init__(self):
        self.__users = {}
        self.__lock = Lock()
        self.__pid = 42

    @property
    def pid(self):
        self.__lock.acquire()
        pid = self.__pid
        self.__pid += 1
        self.__lock.release()
        return pid

    @property
    def users(self):
        return self.__users

    def add_user(self, username):
        """
        Add a user to the backend
        :param username: Username
        :return: The users sessions
        """
        if username not in self.users:
            self.__users[username] = []
        self.__users[username].append(self._add_session(username))
        return self.users

    def _add_session(self, username):
        """Add a sessions"""
        return {
            "username" : username,
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "memory_info": {
                "rss": 0.0,
                "vms": 0.0,
                "shared": 0.0,
                "text": 0.0,
                "data": 0.0,
                "lib": 0.0,
                "dirty": 0.0
            },
            "pid": self.pid,
            "ppid": 42,
            "create_time": time.time()
        }

    def list_users(self):
        """List connected user"""
        return list(self.__users.keys())

    def user_exist(self, username):
        """User exist"""
        if username in self.users:
            return self.users[username]
        return None

    def nb_user(self):
        """Count the number of connected users"""
        return len(self.users)

    def nb_sessions(self):
        """Count the number of opened sessions"""
        nb = 0
        for key, value in self.users.items():
            nb += value
        return nb

    def agent_route(self, app, interval=60):
        """
        Complete Flask app for MookBackend
        :param app: Flask app to use
        :return:
        """

        monitoring = Monitoring(interval=interval)

        @app.route("/v1/monitoring")
        def serve_monitoring():
            return json.dumps(monitoring.data)

        @app.route("/v1/sessions")
        def serve_sessions():
            tmp = []
            for i, v in self.users.items():
                tmp = tmp + v
            return json.dumps(tmp)

        @app.route("/v1/ping")
        def ping():
            """Just a ping"""
            return "OK"

    def backend_route(self, app):
        """
        Add route to simulate a backend
        :param app: The Flask object to use
        :return:
        """

        @app.route("/")
        def root():
            # Get the user sessions
            username = request.args.get("MAAT_USERNAME")

            if username:
                user = self.user_exist(username)
                if user is None:
                    user = self.add_user(username)
                return json.dumps(user)
            return "No user"

        @app.route("/add_sessions/<username>")
        def add_user(username):
            self.add_user(username)
            return redirect("/?MAAT_USERNAME=%s" % username)

        @app.route("/rm_session/<username>")
        def rm_session(username):
            if username not in self.users:
                return "No session found for this user"
            try:
                self.users[username].pop()
                print("Remove a instance for this user")
            except Exception as e:
                print(str(e))
            if len(self.users) == 0:
                self.users.pop(username)
                return "No sessions left for user '%s'" % username
            return "%s session left for the user '%s'" % (len(self.users[username]), username)

        @app.route("/clean/<username>")
        def clean_user(username):
            if username not in self.users:
                return "No session found for this user"
            self.users.pop(username)


def create_fake_pls_backend(host="0.0.0.0", port=5000, interval=30):
    """
    Create a fake PLS backend. This function will Block!!!!!!!!
    :param host: The host to listen on
    :param port: The port to listen on
    :param interval: Interval to update the resource monitoring
    :return:
    """
    app = Flask("Maât-FakePLSBackend")

    fake_pls = FakePLSBackend()

    fake_pls.agent_route(app, interval=interval)
    fake_pls.backend_route(app)

    app.run(host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Maât agent")
    parser.add_argument("-i", "--interval", default=60, type=int, help="Interval between each refresh of data")
    parser.add_argument("-o", "--host", default="0.0.0.0", type=str, help="Host to listen to")
    parser.add_argument("-p", "--port", default=5005, type=int, help="Port to listen to")

    args = parser.parse_args()

    create_fake_pls_backend(host=args.host, port=args.port, interval=args.interval)