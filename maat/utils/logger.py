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
from logging.handlers import RotatingFileHandler


def create_logger(filename="mylog.log", level=logging.INFO, console=True):
    """http://sametmax.com/ecrire-des-logs-en-python/"""
    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(message)s')
    file_handler = RotatingFileHandler(filename, 'a', 1000000, 1)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # création d'un second handler qui va rediriger chaque écriture de log
    # sur la console
    if console:
        steam_handler = logging.StreamHandler()
        steam_handler.setLevel(level)
        logger.addHandler(steam_handler)

    return logger

# Get a basic logger
logger = logging.getLogger()