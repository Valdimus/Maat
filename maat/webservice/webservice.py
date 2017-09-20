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

    def __init__(self, load_balancer, app=Flask("Maât")):
        self.__app = app
        self.__load_balancer = load_balancer
        self.route()
        self.additional_route()

    @property
    def app(self):
        return self.__app

    @property
    def load_balancer(self):
        return self.__load_balancer

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
            # return self.route_root()
            data = self.route_root()
            return render_template("index.html", **data)

        @self.__app.route("/users")
        def get_users_page():
            return redirect("/")

        @self.__app.route("/add_session")
        @self.login_required
        def add_session():
            """Will create a session"""
            return self.route_add_session()

        # All the api route

        @self.__app.route("/api/v1/user_info")
        def user_info():
            return json.dumps(self.route_root())

        @self.__app.route("/api/v1/summary")
        @self.__app.route("/api/v1/summary/<backend>")
        def summary(backend=None):
            """Will list all backends"""
            return self.route_backends()

        @self.__app.route("/api/v1/backends")
        @self.__app.route("/api/v1/backends/<backend>")
        def backends(backend=None):
            """Will list all backends"""
            return json.dumps(self.route_monitoring(backend))

        @self.__app.route("/api/v1/users")
        @self.__app.route("/api/v1/users/<backend>")
        def list_users(backend=None):
            """List all conencted user"""
            return self.route_list_user()

        @self.__app.route("/api/v1/monitor")
        @self.__app.route("/api/v1/monitor/<backend>")
        def monitor_all(backend=None):
            return json.dumps(self.load_balancer.monitoring(backend))

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

        @self.__app.route("/css/<path:path>")
        def send_css(path):
            return send_from_directory('css', path)

        @self.__app.route("/monitoring")
        def monitor():
            data = {}
            return render_template('monitoring.html', **data)


        @self.__app.route("/view/monitor")
        @self.__app.route("/view/monitor/<backend>")
        def view_monitor_all(backend=None):
            d = "/" + backend if backend is not None else ""
            data = {
                "backend": backend,
                "backends": [ x.to_dict() for x in self.load_balancer.backends],
                "data": self.load_balancer.monitoring(backend),
                "update_url": "/api/v1/monitor%s" % d
            }
            return render_template('monitoring.html', **data)

        @self.__app.route("/api/v1/backends_sum")
        def backends_sum():
            return json.dumps(self.sum_backend())

    def sum_backend(self):
        data = {
            "cpu_percent": 0.0,
            "cpu_nb": 0,
            "memory_total": 0,
            "memory_used": 0,
            "swap_used": 0,
            "swap_total": 0,
            "backend_used": 0,
            "backend_total": 0
        }

        for backend in self.load_balancer.backend_manager.to_list():
            data["cpu_percent"] += backend.host("cpu_percent")
            data["cpu_nb"] += backend.host("cpu_nb")
            data["memory_used"] += backend.host("memory_used")
            data["memory_total"] += backend.host("memory_total")
            data["swap_used"] += backend.host("swap_used")
            data["swap_total"] += backend.host("swap_total")
            data["backend_used"] += 1

        temp = data["backend_used"] if data["backend_used"] > 0 else 1
        data["cpu_percent"] = round(data["cpu_percent"] / temp, 3)
        data["backend_total"] += len(self.load_balancer.backend_manager.to_list(all_backends=True))
        data["memory_total"] = round(data["memory_total"] / 1000000000, 3)
        data["swap_used"] = round(data["swap_used"] / 1000000000, 3)
        data["memory_used"] = round(data["memory_used"] / 1000000000, 3)
        data["swap_total"] = round(data["swap_total"] / 1000000000, 3)
        return data

    def additional_route(self):
        pass

    def route_redirect(self, backend_name):
        """Will do the redirection to the corresponding backend"""
        # get the session of the user
        for backend in self.load_balancer.backend_manager.to_list():
            if backend.name == backend_name:
                return redirect(backend.service.url())
        return redirect("/")

    def route_root(self):
        data_src = self.load_balancer.backend_manager.user_sessions_by_backend(self.username())

        cpu_percent = 0.0
        memory = 0
        nb_process = 0
        processes = []
        nb_backend = 0
        memory_total = 0.0
        swap_total = 0.0
        for backend, backend_processes in data_src.items():

            m_backend = self.load_balancer.backend_manager.get(backend)

            backend_core = m_backend.host("cpu_nb")
            nb_backend += 1

            memory_total += m_backend.host("memory_total")
            swap_total += m_backend.host("swap_total")

            for backend_process in backend_processes:
                processes.append({
                    "backend": '<a target="_blank" href="/redirect/%s">%s</a>' % (backend, backend),
                    "project": '<a target="_blank" href="/redirect/%s">%s</a>' % (backend, backend_process["cwd"]),
                    "cpu": str(backend_process['cpu_percent']),
                    "memory": str(round(backend_process['memory_info']['rss'] / 1000000000, 3))
                })

                nb_process += 1
                cpu_percent += backend_process["cpu_percent"] / backend_core
                memory += backend_process["memory_info"]["rss"]
        return {
            "processes": processes,
            "nb_process": nb_process,
            "nb_backend_use": nb_backend,
            "memory": round(memory / 1000000000, 3),
            "memory_total": round(memory_total / 1000000000, 3),
            "swap_total": round(swap_total / 1000000000, 3),
            "max_process": self.load_balancer.max_sessions_by_user,
            "cpu_percent": cpu_percent
        }

    def route_monitoring(self, backend=None):
        return self.load_balancer.backend_manager.monitoring_host(backend)

    def route_add_session(self):
        """Will create a session"""
        try:
            backend = self.load_balancer.balance(self.username())
            return redirect("/redirect/%s" % backend.name)
        except Exception as e:
            print("Error %s" % str(e))
            return redirect("/")

    def route_backends(self):
        """Will list all backends"""
        tmp = []
        for backend in self.load_balancer.backend_manager.to_list():
            tmp.append(backend.to_dict())
        return json.dumps(tmp)

    def route_nb_users(self):
        """Count the number of connected user"""
        return json.dumps(self.load_balancer.backend_manager.nb_process())

    def route_list_user(self):
        """List all conencted user"""
        return json.dumps(self.load_balancer.backend_manager.list_user())