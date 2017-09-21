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

import logging
import operator


class LoadBalancer:
    """
    LoadBalancer is the class that will choose on witch backend an user should have a session.
    """

    def __init__(self, backend_manager, max_sessions_by_user=1, max_attempt_nb=3, logger=None):
        """
        :param backend_manager: The backend manager to use
        :param max_sessions_by_user: The maximum session for an user
        :param max_attempt_nb: The number of time that we will try to create a session on an agent before force it
        :param logger:
        """
        self.__backend_manager = backend_manager
        self.__max_sessions_by_user = max_sessions_by_user
        self.__max_attempt_nb = max_attempt_nb
        self.__logger = logger if logger is not None else logging.getLogger(
            "%s:%s" % (__name__, self.__class__.__name__)
        )

    @property
    def backend_manager(self):
        """Get the backend manager"""
        return self.__backend_manager

    @property
    def max_sessions_by_user(self):
        """Get the max sessions for an user"""
        return self.__max_sessions_by_user

    @property
    def max_attempt_nb(self):
        """Get the maximum number of attempt before force the creation of a new session on a backend"""
        return self.__max_attempt_nb

    def found_lowest_backend_name(self, backends):
        """
        Found the lowest backend for an user
        :param backends: The backend with the number of sessions open for the user on it
        :return: Backend, or None if it not found a suitable backend
        """
        # Sort the user backends
        sorted_user_backends = sorted(backends.items(), key=operator.itemgetter(1))

        # Sort the available backend
        sorted_backends = sorted(self.backend_manager.nb_all_by_backend().items(), key=operator.itemgetter(1))

        for backend_name, _ in sorted_backends:

            if backend_name in [i for i, v in sorted_user_backends]:
                return backend_name, self.backend_manager.get(backend_name).nb()

        return None

    def balance(self, username):
        """
        Choose a backend for an user
        :param username:
        :return:
        """
        attempt_number = 0

        while attempt_number < self.max_attempt_nb + 1:
            attempt_number += 1

            backend, backend_nb = self.choose_backend(username)

            # Check if the service is available
            if backend.service.available:
                self.__logger.info("Ask backend %s if user %s can have a request session on it" % (backend.name, username))

                if backend.agent.add_request(username, backend_nb, force=attempt_number == self.max_attempt_nb) is None:
                    self.__logger.error("Impossible to ask the backend %s" % backend.name)
                    continue

                self.__logger.info("Backend %s is ok for user %s" % (backend.name, username))
                return backend

            self.__logger.error("Backend %s failed for user %s" % (backend.name, username))

        self.__logger.error("Impossible to get a backend for user '%s'" % username)
        return None

    def choose_backend(self, username):
        """
        Choose a backend for this user
        :param username:
        :return:
        """

        # Check if the user don't already have a request on a host

        # Check if the user have reach the user limit
        if self.backend_manager.all_nb_user_sessions(username) >= self.max_sessions_by_user:
            msg = "User %s have reach the max sessions by user" % username
            self.__logger.info(msg)
            raise Exception(msg)

        # Search a session for a user
        backend_sessions = self.backend_manager.nb_user_all_by_backend(username)

        # Only take suitable backend for this user
        restricted_backend = {}
        for backend, value in backend_sessions.items():
            if not self.backend_manager.get(backend).user_reach_limit(username):
                restricted_backend[backend] = value
        backend_sessions = restricted_backend

        self.__logger.info("Available backends for user %s are %s" % (username, backend_sessions))

        lowest_backend_name, backend_nb = self.found_lowest_backend_name(backend_sessions)

        if lowest_backend_name is None:
            msg = "Impossible to found a suitable backend for user %s" % username
            self.__logger.error(msg)
            raise Exception(msg)

        self.__logger.info("Found the backend %s for user %s" % (lowest_backend_name, username))
        return self.backend_manager.get(lowest_backend_name), backend_nb

    def nb(self):
        """Return request + processes number for all available backend"""
        return sum([i.nb() for i in self.backend_manager.to_list()])

    def nb_process(self):
        """Return processes number for all available backend"""
        return sum([i.nb_process() for i in self.backend_manager.to_list()])
