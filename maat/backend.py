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
# Date: 20/03/2017

import logging
from maat import CachedData, HTTPAgentResource


class Backend:
    """
    A backend is the client part of an agent. It allow you to get some information about the agent, like processes and
    requests that are currently on it.
    """

    def __init__(
            self, name, service, agent, version="v1", interval=1.0, max_session_by_user=1
    ):
        """
        :param name: The name of the backend
        :param service: The instance of the service you want to loadbalance (A Resource)
        :param agent: The agent resource to use (Must be an AgentResource)
        :param version: The version of the agent
        :param interval: Interval definied to update the agent data
        :param max_session_by_user: The maximum of session that an user can have on the service
        """
        self.__name = name
        self.__service = service
        self.__agent = agent
        self.__service.name = name
        self.__agent.name = "%s-agent" % name
        self.__version = version
        self.__max_session_by_user = max_session_by_user
        self.__last_sessions_timestamp = 0
        self.__last_requests_timestamp = 0

    @property
    def name(self):
        """Get the name of the backend"""
        return self.__name

    @property
    def service(self):
        """Get the service resource"""
        return self.__service

    @property
    def agent(self):
        """Get the agent resource"""
        return self.__agent

    @property
    def data(self):
        """Get the data of the backend"""
        return self.agent.get()

    @property
    def version(self):
        """Get the version of the agent"""
        return self.__version

    @property
    def max_session_by_user(self):
        """Get the maximum session by user"""
        return self.__max_session_by_user

    def user_reach_limit(self, username):
        """Chek if an user a reach the limit"""
        return self.user_nb_processes(username) > self.max_session_by_user

    def available(self):
        """Check if the backend is available"""
        return self.service.available and self.agent.available()

    def processes(self, username):
        """Get all processes of the backend"""
        if username in self.data["processes"]:
            return self.data["processes"][username]
        return []

    def host(self, name=None):
        """Get of information"""
        host_data = self.data["host"]
        if name is None:
            return host_data
        if name not in host_data:
            return None
        return host_data[name]

    def users(self):
        """Get all user connected to the backend"""
        temp = self.data["processes"].keys()
        for i in self.data["requests"].keys():
            if i not in temp:
                temp.append(i)

        return temp

    def nb_process(self):
        """Get the number of processes running on the backend"""
        return self.data["nb_process"]

    def nb_user(self):
        """Get the number of user currently using the backend"""
        return len(self.users())

    def nb_requests(self):
        """Get the number of requests"""
        nb = 0
        for i, v in self.requests().items():
            nb += len(v)
        return nb

    def processes_timestamp(self):
        """Get the processes timestamp  (time since last update)"""
        return self.data["processes_timestamp"]

    def requests(self):
        """Get all requests currently available on the backend"""
        return self.data["requests"]

    def user_nb_request(self, username):
        """Get the number of request on the agent for this user"""
        if username in self.requests():
            return len(self.requests()[username])
        return 0

    def user_nb_all(self, username):
        """Get all the number of processes and request on the agent for this user"""
        return self.user_nb_request(username) + self.user_nb_processes(username)

    def requests_timestamp(self):
        """Get the request timestamp (time since last update)"""
        return self.data["requests_timestamp"]

    def nb(self):
        """Get the number of all requests + processes on the backend"""
        return self.data["nb"]

    def timestamp(self):
        """Get the timestamp of the agent (time since last update)"""
        return self.data["timestamp"]

    def user_nb_processes(self, username):
        """Get the number of process for an user on this backend"""
        return len(self.processes(username))

    def to_dict(self):
        """Convert this object to a dict"""
        return {
            "name": self.name,
            "hostname": self.service.host,
            "url": self.service.url(),
            "available": self.available(),
            "data": self.data
        }