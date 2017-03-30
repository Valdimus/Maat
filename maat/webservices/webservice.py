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

import json
from flask import Flask, redirect, send_from_directory, render_template
from gevent.wsgi import WSGIServer


class Webservice:
    """Maât webservice"""

    def __init__(self, session_manager, app=Flask("Maât")):
        self.__app = app
        self.__session_manager = session_manager
        self.route()
        self.additional_route()

    @property
    def app(self):
        return self.__app

    @property
    def session_manager(self):
        return self.__session_manager

    def login_required(self, funct):
        """Override this method to add authentification to the webinterface"""
        return funct

    def username(self):
        """Get the usename of the client. This function only can be used int the context of flask request"""
        return "test"

    def run(self, host="0.0.0.0", port=5000):

        http_server = WSGIServer((host, port), self.__app)
        http_server.serve_forever()

    def route(self):

        @self.__app.route("/redirect/<backend_name>")
        @self.login_required
        def redirect_toto(backend_name):
            """Will do the redirection to the corresponding backend"""
            return self.route_redirect(backend_name)

        @self.__app.route("/")
        @self.login_required
        def root():
            """Will list available session or permit to create one"""
            return self.route_root()

        @self.__app.route("/add_session")
        @self.login_required
        def add_session():
            """Will create a session"""
            return self.route_add_session()

        # All the api route

        @self.__app.route("/api/v1/summary")
        @self.__app.route("/api/v1/summary/<backend>")
        def summary(backend=None):
            """Will list all backends"""
            return self.route_backends()

        @self.__app.route("/api/v1/backends")
        @self.__app.route("/api/v1/backends/<backend>")
        def backends(backend=None):
            """Will list all backends"""
            return self.route_backends()

        @self.__app.route("/api/v1/users")
        @self.__app.route("/api/v1/users/<backend>")
        def list_users(backend=None):
            """List all conencted user"""
            return self.route_list_user()

        @self.__app.route("/api/v1/monitor")
        @self.__app.route("/api/v1/monitor/<backend>")
        def monitor_all(backend=None):
            return json.dumps(self.session_manager.monitoring(backend))

        @self.__app.route("/api/v1/sessions")
        @self.__app.route("/api/v1/sessions/<username>")
        def get_sessions(username=None):
            return username

        @self.__app.route("/api/v1/nb_sessions")
        @self.__app.route("/api/v1/nb_sessions/<username>")
        def nb_sessions(username=None):
            """Get the number of opened sessions"""
            return "Todo"

        @self.__app.route("/api/v1/nb_users")
        @self.__app.route("/api/v1/nb_users/<backend>")
        def nb_users(backend=None):
            """Count the number of connected user"""
            return self.route_nb_users()

        @self.__app.route("/js/<path:path>")
        def send_js(path):
            return send_from_directory('js', path)

        @self.__app.route("/view/monitor")
        @self.__app.route("/view/monitor/<backend>")
        def view_monitor_all(backend=None):
            d = "/" + backend if backend is not None else ""
            data = {
                "backend": backend,
                "backends": [ x.to_dict() for x in self.session_manager.backends],
                "data": self.session_manager.monitoring(backend),
                "update_url": "/api/v1/monitor%s" % d
            }
            return render_template('monitoring.html', **data)

        @self.__app.route("/api/v1/backends_sum")
        def backends_sum():
            return json.dumps(self.session_manager.backends_sum())

    def additional_route(self):
        pass

    def route_redirect(self, backend_name):
        """Will do the redirection to the corresponding backend"""
        # get the session of the user
        for backend in self.session_manager.backends:
            if backend.name == backend_name:
                return redirect(backend.url())
        return redirect("/")

    def route_root(self):
        """Will list available session or permit to create one"""
        ret = "<h1>Your sessions</h1>"
        for session in self.session_manager.get_user_sessions(self.username()):
            ret += '<a href="/redirect/%s">Session on backend %s, pid=%s</a><br />' % (
                session.backend.name, session.backend.name, session.pid
            )
        ret += '<a href="/add_session">Create a new session</a>'
        return ret

    def route_add_session(self):
        """Will create a session"""
        try:
            backend = self.session_manager.add_session(self.username())
            return redirect("/redirect/%s" % backend.name)
        except Exception:
            return redirect("/")

    def route_backends(self):
        """Will list all backends"""
        tmp = []
        for backend in self.session_manager.backends:
            tmp.append(backend.to_dict())
        return json.dumps(tmp)

    def route_nb_users(self):
        """Count the number of connected user"""
        return json.dumps(self.session_manager.nb_users)

    def route_list_user(self):
        """List all conencted user"""
        return json.dumps(self.session_manager.connected_users)