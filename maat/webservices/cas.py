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

from flask_cas import CAS, login_required
from maat.webservices import Webservice


class CASWebservice(Webservice):
    """
    Cas authentification

    See https://github.com/cameronbwhite/Flask-CAS
    """

    def __init__(
            self, server, *args, after_login="/", login_route="/cas/login",
            logout_route="/cas/logout", validate_route="/cas/serviceValidate", **kwargs
    ):
        Webservice.__init__(*args, **kwargs)
        self.__cas = CAS(self.app)
        self.app.config["CAS_SERVER"] = server
        self.app.config["CAS_AFTER_LOGIN"] = after_login
        self.app.config["CAS_LOGIN_ROUTE"] = login_route
        self.app.config["CAS_LOGOUT_ROUTE"] = logout_route
        self.app.config["CAS_VALIDATE_ROUTE"] = validate_route

    def login_required(self, func):
        """Call login_required of CAS module"""
        return login_required(func)

    def username(self):
        """Get the username of the client from session"""
        return self.__cas.username
