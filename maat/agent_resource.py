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

import os
import json
from maat import Resource, CachedData


class AgentResource:
    """
    I need this class to make an abstraction of the way to get the data from the agent.
    In production mode, it will use HTTP, but for testing purpose I need to have a simple way
    to communicate with an agent.
    """

    def get(self):
        """Get the data of the agent"""
        return {
            "processes": {},
            "processes_timestamp": 0,
            "requests": {},
            "requests_timestamp": 0,
            "nb": 0,
            "nb_process": 0,
            "nb_requests": 0,
            "timestamp": 0
        }

    def add_request(self, username, know_value, force=False):
        """
        Add a request on the agent
        :param username: The name of the user
        :param know_value: The number of process and request that you know want you decide to use this backend
        :param force: Force the choose of this backend
        :return: boolean
        """
        raise NotImplementedError

    def available(self):
        """
        Check that the resource is available
        :return boolean
        """
        return True


class HTTPAgentResource(AgentResource):
    """
    Get the data from a agent using HTTP. This class will cache this data.
    """

    def __init__(self, host, port, interval=1, version="v1", name="HTTPAgentResource", **kwargs):
        """

        :param resource: The HTTP Resource to the agent
        """
        kwargs["ping_cmd"] = "/ping"
        kwargs["default_url"] = "/%s" % version

        self.__version = version
        self.__resource = Resource(host, port, **kwargs)
        self.__name = name
        self.__data = CachedData(
            default_data={
                "processes": {},
                "processes_timestamp": 0,
                "requests": {},
                "requests_timestamp": 0,
                "nb": 0,
                "nb_process": 0,
                "nb_requests": 0,
                "timestamp": 0
            }, interval=interval, update_fct=self._update_data, no_previous_data=True, default_on_failure=True,
            name="Backend-%s" % name
        )

    @property
    def resource(self):
        """Get the resource"""
        return self.__resource

    @property
    def version(self):
        """Get the version of the agent"""
        return self.__version

    def url(self, path):
        return "/%s/%s" % (self.version, path)

    def get(self):
        """Get the data of the agent"""
        return self.__data.data

    def _update_data(self, previous_data):
        """Update function use to cache the data from the agent"""
        data = self.resource.cmd(self.url("data"))
        if data is None:
            raise Exception("Impossible to get the data")
        return  data

    def add_request(self, username, know_value, force=False):
        """
        Add a request on the agent
        :param username: The name of the user
        :param know_value: The number of process and request that you know want you decide to use this backend
        :param force: Force the choose of this backend
        :return: boolean
        """
        return self.resource.cmd(self.url("new_requests/%s/%s/%s" % (username, know_value, int(force))))

    def available(self):
        """
        Check that the resource is available
        :return boolean
        """
        return self.resource.available


class DirectAgentResource(AgentResource):
    """Just a way to communicate with the agent without passing with HTTP (for testing purpose)"""

    def __init__(self, agent):
        """
        :param agent: The agent to use
        """
        self.__agent = agent
        self.__available = True

    def __del__(self):
        """Stop the agent thread and delete it"""
        self.__agent.stop()
        del self.__agent

    @property
    def agent(self):
        """Get the agent"""
        return self.__agent

    def set_available(self, available):
        """Set the availability of the agent (for testing purpose)"""
        self.__available = available

    def available(self):
        """
        Check that the resource is available
        :return boolean
        """
        return self.__available

    def get(self):
        """Get the data of the agent"""
        return json.loads(self.agent.data)

    def add_request(self, username, know_value, force=False):
        """
        Add a request on the agent
        :param username: The name of the user
        :param know_value: The number of process and request that you know want you decide to use this backend
        :param force: Force the choose of this backend
        :return: boolean
        """
        return self.agent.add_process_request(username, know_value, force=force)
