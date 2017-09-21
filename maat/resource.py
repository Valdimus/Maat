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

import re
import json
import logging
import requests
from maat import CachedData


class Resource(object):
    """
    A Ressource, is just a way to make a request on a service (HTTP for example). It check if the resource if available
    and let you make call on the HTTP server.
    """

    def __init__(
            self, host, port, protocol="http", timeout=1, ping_cmd="/", ping_interval=1, default_url="/", name="",
            logger=None
    ):
        self.__name = name
        self.__host = host
        self.__port = port
        self.__protocol = protocol
        self.__timeout = timeout
        self.__ping_cmd = ping_cmd
        self.__ping_interval = ping_interval
        self.__available = CachedData(
            default_data=False, interval=self.__ping_interval, update_fct=self.ping,
            name="Ressource-%s" % name
        )
        self.__default_url = default_url
        self.__logger = logger if logger is not None else logging.getLogger(
            "%s:%s" % (__name__, self.__class__.__name__)
        )
        print(self.__default_url)

    @property
    def name(self):
        """Get the name"""
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def host(self):
        """Get the host"""
        return self.__host

    @host.setter
    def host(self, host):
        self.__host = host

    @property
    def port(self):
        """Get the port"""
        return self.__port

    @port.setter
    def port(self, port):
        self.__port = port

    @property
    def protocol(self):
        """Get the protocol"""
        return self.__protocol

    @protocol.setter
    def protocol(self, protocol):
        self.__protocol = protocol

    @property
    def timeout(self):
        """Get the timeout"""
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout):
        self.__timeout = timeout

    @property
    def ping_cmd(self):
        """Get the ping_cmd"""
        return self.__ping_cmd

    @ping_cmd.setter
    def ping_cmd(self, ping_cmd):
        self.__ping_cmd = ping_cmd

    @property
    def available(self):
        return self.__available.data

    @property
    def ping_interval(self):
        """Get the ping_interval"""
        return self.__ping_interval

    @property
    def ping_url(self):
        return self.url(self.ping_cmd)

    def url(self, path=None, default_url=True):
        """
        Get the url to the backend
        :param path: Path to the ressource, if None get the default path
        :param default_url: Use default url
        :return: str
        """
        v = self.__default_url if default_url else ""
        return "%s://%s%s%s" % (
            self.protocol,
            self.host,
            ":%s" % self.port if self.port is not None else "",
            v if path is None else path
        )

    def make_request(self, *args, **kwargs):
        """Make a request to the API"""
        try:
            # Make the call
            r = requests.get(*args, timeout=self.timeout, **kwargs)
            # Raise on error
            r.raise_for_status()
            try:
                return r.json()
            except:
                return r.text
        except Exception as e:
            self.__logger.error("make_request[%s]: %s" % (args, str(e)))
            return None

    def to_dict(self):
        """Convert this object to a dict"""
        return {
            "name": self.name,
            "hostname": self.host,
            "url": self.url(),
            "ping_url": self.ping_url,
            "available": self.available,
            "ping_last_update": self.__available.last_update
        }

    def ping(self, previous_data):
        """Make a ping"""
        request = self.make_request(self.ping_url)

        # Ping Failed
        if request is None:
            if previous_data:
                self.__logger.error("Backend '%s' seems to be dead!" % self.name)
            return False

        # Ping Ok
        if not previous_data:
            self.__logger.info("Backend '%s' is now available!" % self.name)
        return True

    def cmd(self, *args, **kwargs):
        """
        Make a request on the resource
        """
        url = args[0] if len(args) > 0 else None
        to_args = [] if len(args) <= 1 else args[1:]
        return self.make_request(self.url(url), *to_args, **kwargs)

    def __str__(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return self.__str__()


class DummyResource(Resource):

    def __init__(self, result_matrix, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.__logger = logging.getLogger("%s:%s" % (__name__, self.__class__.__name__))
        self.__result_matrix = result_matrix

        if not isinstance(self.__result_matrix, dict):
            self.__logger.error("result_matrix must be a dict!")
            raise Exception("result_matrix must be a dict!")

    def make_request(self, *args, **kwargs):
        """Emulate a call"""
        try:
            url = args[0].split(self.url(default_url=False))[-1] if len(args) > 0 else None

            if url in self.__result_matrix:
                return self.__result_matrix[url]
        except Exception as e:
            print("%s was not found!" % str(e))
        return None


class SuperDummyResource(DummyResource):

    @property
    def available(self):
        return True
