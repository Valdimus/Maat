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

from threading import Lock
from maat.utils import logger

# dict(collection._asdict())


class CachedData:
    """
    I need to maintain data on the webservice, data which is get from external sources. But I don't want to call this
    external every time I want to know the value of the data. So this class is made to solve this problem.
    """

    def __init__(self, interval=0, update_fct=None, default_data=None, default_on_failure=True):
        """
        :param interval: Interval to update the data store in the class
        :param update_fct: Function to us to update the data, if None will use the update function of this class
        :param default_data: Default value to use if it's impossible to update the data
        :param default_on_failure: Use default value on failed
        """
        self.__data = default_data
        self.__default_data = default_data
        self.__default_on_failure = default_on_failure
        if interval >= 0.0:
            self.__interval = interval
        else:
            raise Exception("Interval must be an number >= 0.0")
        self.__update_fct = self.update if update_fct is None else update_fct
        self.__lock = Lock()
        self.__last_update = 0
        self.__failed = False

    @property
    def data(self):
        """
        Get the data and update it if necessary
        :return: The data
        """

        # Check if we have to update the data, and if necessary, do it
        self.__update()

        # Return the data
        return self.__data

    @property
    def force_data(self):
        """
        Force the update and get it
        :return:
        """
        self._update()
        return self.__data

    @property
    def default_data(self):
        return self.__default_data

    @property
    def default_on_failure(self):
        return self.__default_on_failure

    @property
    def interval(self):
        """
        Get the interval between each update
        :return: number
        """
        return self.__interval

    @interval.setter
    def interval(self, interval):
        """
        Set the interval
        :param interval: number
        """
        if interval >= 0.0:
            self.__interval = interval
        else:
            raise Exception("Interval must be an number >= 0.0")

    @property
    def last_update(self):
        """Get the last update"""
        return self.__last_update

    def failed(self):
        """Return the state of the update"""
        return self.__failed

    def update(self, previous_data):
        """
        Update the data store in cache
        :param previous_data: The data that was actually store
        :return: The data
        """
        raise Exception("You don't precise an update function!")

    def __update(self):
        """
        This method check if we have to update the data
        """
        if time.time() - self.__last_update < self.interval:
            return

        # Do the update
        self._update()

    def _update(self):
        """
        This method is use to update the data store in the cache. The lock is necessary because we don't know how
        this class will be use (threading or gevent). So mad it thread safe looks like a good solution for my own sake.
        """

        # Check if an update is not already going on
        if self.__lock.acquire(blocking=False, timeout=-1):
            logger.info("Update data for '%s'" % type(self).__name__)
            try:
                #  Update data
                # Should made a deep copy of data, to pass it to the update method
                self.__data = self.__update_fct(self.__data)
                self.__last_update = time.time()
                self.__failed = False
            except Exception as e:
                # Set default value if necessary
                if self.default_on_failure:
                    self.__data = self.default_data

                self.__failed = True
                logger.error("Impossible to update data '%s' => %s" % (type(self).__name__, str(e)))

            # Relase the lock
            self.__lock.release()
