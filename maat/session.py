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
# Date: 21/03/2017


class Session:
    """Represent an user session on a backend"""

    def __init__(self, backend, username, pid):
        """
        :param backend: Backend on whith the user is conencted
        :param username: The user name
        :param pid: Pid of the session
        """
        self.__backend = backend
        self.__username = username
        self.__pid = pid

    @property
    def backend(self):
        """Get the backend on with the session is"""
        return self.__backend

    @property
    def username(self):
        """Get the username of the session"""
        return self.__username

    @property
    def pid(self):
        """Get the pid of the session"""
        return self.__pid

    @property
    def exist(self):
        """Check if the session exist on the backend"""
        return self.session is not None

    @property
    def session(self):
        """Get the monitoring object"""
        return self.backend.get_user_monitoring_session(self.username, self.pid)

