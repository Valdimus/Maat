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

import time
import logging


class Requests:
    """
    Requests allow us to memorise when a user ask for a new process on the host
    """
    def __init__(self, logger=None):
        self.__requests = {}
        self.__last_update = 0
        self.__logger = logger if logger is not None else logging.getLogger(
            "%s:%s" % (__name__, self.__class__.__name__)
        )

    @property
    def requests(self):
        """Get the requests"""
        return self.__requests

    @property
    def nb(self):
        """Get the number of requests"""
        return sum([len(v) for k, v in self.requests.items()])


    @property
    def last_update(self):
        """Get the last update of the requests"""
        return self.__last_update

    def add(self, username):
        """
        Add the request for the specific user
        :param username: The user name
        :return:
        """
        self.__logger.info("Add a process request for user: '%s'" % username)
        self.__last_update = time.time()
        if username not in self.requests:
            self.requests[username] = []
        self.requests[username].append(self.last_update)

    def rm(self, username, value):
        """
        Remove a request for an user
        :param username: The name of the user
        :param value: The value to remove
        :return:
        """
        if username in self.requests:
            if value in self.requests[username]:
                self.__logger.info("Remove a request %s process for user '%s'" % (username, value))
                self.requests[username].remove(value)
                self.__last_update = time.time()
            if len(self.requests[username]) == 0:
                del self.requests[username]