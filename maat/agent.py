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
# Date: 22/03/2017

from gevent import monkey
monkey.patch_all(thread=False)

import time
import json
from flask import Flask
from gevent.wsgi import WSGIServer
from threading import Lock, Thread
import logging

from maat import ProcessMonitoring, HostMonitoring
from maat import Requests


class MaatAgent(object):
    """
    The Maat agent. This agent is use to monitor the process launch by the service to load balance. It is in charge of:
    - Monitor the process of the service for each user
    - Count the number of users on the service
    - Count the number process of the service for each user
    - Accept new connection for the service
    - Monitor the system usage (Not Implemented Yet)
    """

    def __init__(
            self, process_name, sleep_time=5, process_interval=2.5, max_process_by_user=1, request_time=30,
            logger=None, process_monitoring=ProcessMonitoring, requests=Requests
    ):
        """
        :param process_name: The name of the process to monitor
        :param sleep_time: Time to sleep between each iteration of the run function on the thread
        :param process_interval: The interval between each process list update
        :param max_process_by_user: The max process that an user can have of the service
        :param request_time: The time to wait to accept a request
        :param process_monitoring: The ProcessMonitopring class to use
        :param requests: Requests
        """

        self.__logger = logger if logger is not None else logging.getLogger(
            "%s:%s" % (__name__, self.__class__.__name__)
        )

        # Host Monitoring

        # Session Monitoring
        self.__process_monitoring = process_monitoring(
            process_name=process_name, interval=process_interval, auto_update=False, name="Processes"
        )
        self.__process_monitoring_lu = 0

        self.__host_monitoring = HostMonitoring(
            interval=process_interval, auto_update=False, name="Host"
        )
        self.__host_monitoring_lu = 0

        # This variable can be use to stop the thread
        self.__close = False
        self.__sleep_time = sleep_time

        self.__lock = Lock()

        # Request for a session
        self.__requests = requests()

        # Request Last Update
        self.__requests_lu = 0

        # Cache
        self.__cache = json.dumps({
            # The processes
            "processes": {},
            "nb_process": 0,
            "processes_timestamp": 0,

            # The requests
            "requests": {},
            "requests_timestamp": 0,
            "nb_requests": 0,

            # The total number of processes and requests
            "nb": 0,
            "timestamp": 0
        })

        self.__cache_lu = 0

        # Max process by user
        self.__max_process_by_user = max_process_by_user

        # Last run of the thread
        self.__last_run = 0

        self.__request_time = request_time

        self.__thread = Thread(target=self.run)
        self.__thread.start()

    def __del__(self):
        self.stop()

    @property
    def version(self):
        return "v1"

    @property
    def sleep_time(self):
        """
        Time to sleep between each iteration of the run function on the thread
        :return: time
        """
        return self.__sleep_time

    @property
    def request_time(self):
        return self.__request_time

    @property
    def max_process_by_user(self):
        """
        The maximum of process that the user can have for this service
        :return: number
        """
        return self.__max_process_by_user

    @property
    def data(self):
        """
        The cache data
        :return:
        """
        # Check if we have to do an update
        self.update_cache()
        return self.__cache

    @property
    def process_monitoring(self):
        return self.__process_monitoring

    @property
    def host_monitoring(self):
        return self.__host_monitoring

    @property
    def requests(self):
        return self.__requests

    def cache_need_update(self):
        return (
            self.process_monitoring.last_update != self.__process_monitoring_lu or
            self.requests.last_update != self.__requests_lu or
            self.__host_monitoring_lu != self.__host_monitoring.last_update
        )

    def update_cache(self):
        """Update the cache"""
        if not self.cache_need_update():
            return
        self.__logger.info("Update the cache of the Agent")

        processes = self.process_monitoring.data
        self.__process_monitoring_lu = self.process_monitoring.last_update

        host_monitoring = self.host_monitoring.data

        self.__host_monitoring_lu = self.__host_monitoring.last_update
        self.__requests_lu = self.requests.last_update
        self.__cache_lu = time.time()

        self.__cache = json.dumps({

            # The processes
            "processes_timestamp": self.__process_monitoring_lu,
            "processes": processes["users"],
            "nb_process": processes["nb"],

            # The requests
            "requests": self.requests.requests,
            "nb_requests": self.requests.nb,
            "requests_timestamp": self.__requests_lu,

            # The total number of processes and requests
            "nb": self.requests.nb + processes["nb"],

            # The host
            "host": host_monitoring,
            "host_timestamp": self.__host_monitoring_lu,

            "timestamp": self.__cache_lu,
        }, indent=4)

    def add_process_request(self, username, know_value, force=False):
        """
        Create a request for a specific user
        :param username: The name of the user
        :param know_value: The number of know session on this host
        :param force: If the loadbalancer realy want a session on this host
        :return: boolean, if True the user is allow to create a process on this host
        """

        with self.__lock:
            if force:
                self.__logger.info("Force the creation of a request for the user: '%s'", username)
                self.requests.add(username)
                return True

            # Get the user object
            user = self.requests.requests[username] if username in self.requests.requests else None

            # Check if the user reach the maximum process on this host
            size = len(user) if user is not None else 0
            size += len(self.process_monitoring.data["users"][username]) if username in self.process_monitoring.data["users"] else 0

            if size >= self.max_process_by_user:
                self.__logger.info("User '%s' have reach the maximum of process on this host!" % username)
                return False

            session_nb = self.requests.nb + self.process_monitoring.data["nb"]

            # Check is the value use to select this host is not deprecated
            if know_value < session_nb + 3 and know_value > session_nb - 3:
                self.requests.add(username)
                return True
            else:
                self.__logger.error("The value %s is deprecated, new value is %s" % (know_value, session_nb))

        return False

    def update_request(self):
        """
        Update the request sessions
        :return:
        """

        # Request to delete
        to_del = {}

        with self.__lock:

            self.__logger.debug("Update Request: " % self.requests.requests)

            # Search request to remove
            for username, timestamp_list in self.requests.requests.items():
                to_del[username] = []
                for timestamp in timestamp_list:
                    if time.time() - timestamp >= self.request_time:
                        self.__logger.debug("A request for the user %s as experied" % username)
                        to_del[username].append(timestamp)
                        continue

                    if username not in self.process_monitoring.data["users"]:
                        continue

                    user_sessions = self.process_monitoring.data["users"][username]

                    # Check that the request is valid
                    # if user_sessions["nb"] >= self.__max_process_by_user:
                    #     self.__logger.info("User '%s' have reach the maximum session by user, so delete this request" % username)
                    #     to_del.append(username)
                    #     continue

                    # Check if a session have been created to answer to this request
                    for session in user_sessions:
                        self.__logger.debug("Compare request %s with process create at %s for user '%s'" % (
                            timestamp, session["create_time"], session["username"]
                        ))
                        if session["create_time"] >= timestamp:
                            self.__logger.info("Remove request %s for user '%s', found session created at %s" % (
                                timestamp, session["username"], session["create_time"]
                            ))
                            to_del[username].append(timestamp)
                            continue

            # Remove request
            for username, timestamps in to_del.items():
                for timestamp in timestamps:
                    self.requests.rm(username, timestamp)

    def stop(self):
        """Stop the thread"""
        self.__logger.info("Stop the thread")
        self.__close = True
        self.__thread.join()

    def run(self):
        """Run the thread"""

        while not self.__close:
            # Update the sessions monitoring
            self.process_monitoring.update()

            # Update Host
            self.host_monitoring.update()

            # THIS MUST BE FAST, VERY FAST
            self.update_request()

            # No Wait if we have to close
            if self.__close:
                break

            # Wait
            time.sleep(self.__sleep_time)

    def create_api(self, app):
        """
        Create route to the Flask application
        :param app:
        :return:
        """

        @app.route("/info")
        def info():
            return json.dumps({
                "process_name": self.process_monitoring.process_name,
                "version": self.version
            })

        @app.route("/%s/data" % self.version)
        def data():
            return self.data

        @app.route("/%s/new_requests/<string:username>/<int:know_value>" % self.version)
        @app.route("/%s/new_requests/<string:username>/<int:know_value>/<int:force>" % self.version)
        def add_request(username, know_value, force=0):
            return json.dumps(self.add_process_request(username, know_value, force=force > 0))

        @app.route("/ping")
        @app.route("/%s/ping" % self.version)
        def ping():
            return "OK"


def create_agent_api(host, port, agent, application=None):
    """
    Create the agent webservice
    :param host: Host to listen to
    :param port: Port to listen to
    :param agent: The agent to expose
    :param application: Flask application to use (default is None, it will create one)
    :return: Noting
    """
    app = Flask("Maât-Agent") if application is None else application

    agent.create_api(app)

    http_server = WSGIServer((host, port), app)
    http_server.serve_forever()