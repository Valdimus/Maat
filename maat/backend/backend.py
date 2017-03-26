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

import json
import requests
from maat import logger, CachedData


class Backend:
    """
    This class represent a service that you want to load balance. It gives you some information about the service, like
    his availability
    """

    def __init__(
            self, hostname="127.0.0.1", port=None, protocol="http", path="", name=None, timeout=0.5, ping_path=None,
            ping_interval=1
    ):
        """
        :param hostname: The host name of the backend
        :param port: Port to the service
        :param protocol: Protocol to use
        :param path: Path to the ressource
        :param name: Name of the backend
        :param timeout: Timeout to consider the backend unavaible
        :param ping_path: Path to use to make a ping, if None will use path
        """
        self.__hostname = hostname
        self.__port = port
        self.__protocol = protocol
        self.__path = path
        self.__name = hostname if name is None else name
        self.__timeout = timeout
        self.__ping_path = path if ping_path is None else ping_path
        self.__ping_interval = ping_interval
        self.__available = CachedData(data=False, interval=self.__ping_interval, update_fct=self._ping)

    @property
    def hostname(self):
        return self.__hostname

    @property
    def port(self):
        return self.__port

    @property
    def protocol(self):
        return self.__protocol

    @property
    def path(self):
        return self.__path

    @property
    def name(self):
        return self.__name

    @property
    def timeout(self):
        return self.__timeout

    @property
    def ping_path(self):
        return self.__ping_path

    @property
    def ping_interval(self):
        return self.__ping_interval

    @property
    def available(self):
        return self.__available.data

    @property
    def ping_url(self):
        """Get the url to ping on"""
        return self.url(self.ping_path)

    def url(self, path=None):
        """
        Get the url to the backend
        :param path: Path to the ressource, if None get the default path
        :return: str
        """
        return "%s://%s%s%s" % (
            self.protocol,
            self.hostname,
            ":%s" % self.port if self.port is not None else "",
            self.path if path is None else path
        )

    def make_request(self, *args, **kwargs):
        """Make a request to the API"""
        try:
            # Make the call
            r = requests.get(*args, timeout=self.timeout, **kwargs)
            # Raise on error
            r.raise_for_status()
            return r
        except Exception as e:
            logger.error(str(e))
            return None

    def to_dict(self):
        """Convert this object to a dict"""
        return {
            "name": self.name,
            "hostname": self.hostname,
            "url": self.url(),
            "ping_url": self.ping_url,
            "available": self.available
        }

    def _ping(self, previous_data):
        """Make a ping"""
        request = self.make_request(self.ping_url)

        # Ping Failed
        if request is None:
            if previous_data:
                logger.error("Backend '%s' seems to be dead!" % self.name)
            return False

        # Ping Ok
        if not previous_data:
            logger.info("Backend '%s' is now available!" % self.name)
        return True

    def __str__(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return self.__str__()
