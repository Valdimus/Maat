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
from copy import deepcopy
from threading import Lock

class CachedData(object):
    """
    A CachedData is just a way to cache some data that can be expensive to get. No lock is needed because I never use
    the data in the update function. If I had to know the actual data, I pass a deepcopy of it to the udpate function.
    """

    def __init__(
            self, update_fct=None, default_data=None, default_on_failure=False, interval=1.0, no_previous_data=False,
            auto_update=True, name=None, logger=None
    ):
        """
        :param update_fct: Function to use to update the data. Must have as parameter "previous_data"
        :param default_data: The default data to use.
        :param default_on_failure: Use the default value on failure
        :param interval: Interval fo updating the data
        :param no_previous_data: Don't make a deepcopy of the previous data
        :param auto_update: Update the data when you get the cache value (only if we have to)
        :param name: The name of the cached data
        :param logger: The logger to use
        """
        self.__update_fct = self.update_data if update_fct is None else update_fct
        self.__data = default_data
        self.__failed = False
        self.__last_update = 0
        self.__default_data = default_data
        self.__default_on_failure = default_on_failure
        self.__interval = interval
        self.__no_previous_data = no_previous_data
        self.__auto_update = auto_update
        self.__name = self.__class__.__name__ if name is None else name
        self.__logger = logger if logger is not None else logging.getLogger(
            "%s:%s" % (__name__, self.__class__.__name__)
        )
        self.__lock = Lock()

    @property
    def data(self):
        """
        Get the data
        The update is do only if you have set the auto_update parameter to True
        :return: data
        """
        if self.auto_update:
            self.update()
        return self.__data

    @property
    def last_update(self):
        """
        Get the last update time
        :return: time
        """
        return self.__last_update

    @property
    def default_data(self):
        """
        Get the default data
        :return: data
        """
        return self.__default_data

    @property
    def default_on_failure(self):
        """
        Know if we have to use the default data on failure
        :return: boolean
        """
        return self.__default_on_failure

    @property
    def failed(self):
        """
        A way to know if we successfully update the data
        :return: boolean
        """
        return self.__failed

    @property
    def update_fct(self):
        """
        The function use to update the data
        :return: a function
        """
        return self.__update_fct

    @property
    def interval(self):
        """
        Get the update interval
        :return: time - seconds
        """
        return self.__interval

    @property
    def no_previous_data(self):
        """
        Know if we have to use the previous data as a parameter for the update function
        :return: boolean
        """
        return self.__no_previous_data

    @property
    def auto_update(self):
        """
        Know if the data is update when you try to get it.
        :return: boolean
        """
        return self.__auto_update

    @property
    def name(self):
        """
        Get the name of the cached Data
        :return: string
        """
        return self.__name

    def update_data(self, previous_data):
        """
        This function is the default one us to update the data. It just a way to use this class as a super class and just
        overide this function to update the data
        :param previous_data: the previous data, can be None
        :return: the new data
        """
        raise NotImplementedError

    def update(self):
        """
        Do an update only if it is necessary
        :return:
        """
        if self.__lock.acquire(blocking=False):
            try:
                time_since_last_update = time.time() - self.last_update
                if time_since_last_update > self.interval:
                    self.__logger.debug("Last update of CachedData '%s' is %s, so we have to update it!" % (
                        self.name, time_since_last_update
                    ))
                    self.do_update()
            except Exception as e:
                self.__logger.erro(str(e))
            finally:
                self.__lock.release()

    def do_update(self):
        """
        Do the update
        :return: The new data
        """
        # Get a copy of the previous data
        previous_data = deepcopy(self.__data) if not self.no_previous_data else None
        self.__logger.debug("Try to update CachedData '%s', previous_data=%s, last_update=%s" % (
            self.name, previous_data, self.last_update
        ))
        try:
            self.__data = self.__update_fct(previous_data)
            self.__last_update = time.time()
            self.__failed = False
            self.__logger.debug("Update CachedData '%s', previous_data=%s, last_update=%s with new value '%s'" % (
                self.name, previous_data, self.last_update, self.__data
            ))
            self.__logger.info("Update CachedData '%s' successfully!" % self.name)
        except Exception as e:
            self.__failed = True
            if self.default_on_failure:
                self.__data = self.__default_data
            self.__logger.error("Impossible to update CachedData '%s', previous_data=%s, last_update=%s, error=%s" % (
                self.name, previous_data, self.last_update, str(e)
            ))
