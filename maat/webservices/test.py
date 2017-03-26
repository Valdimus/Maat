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
from flask import Flask, redirect, escape, session, request
from maat.webservices import Webservice


class TestWebservice(Webservice):
    """Maât webservice"""

    def additional_route(self):
        """Additional route for test authentification"""

        @self.app.route('/info')
        def index():
            if 'username' in session:

                username_active = escape(session["username"])
                ret = 'Active User: <a href="/test/%s">%s</a><br />' % (username_active, username_active)
                liste = json.loads(session['users'])
                print(liste)
                if liste is not None:
                    for i in json.loads(session["users"]):
                        mi = escape(i)
                        if mi == username_active:
                            continue
                        ret += 'Test: <a href="/test/%s">%s</a><br />' % (mi, mi)
                ret += '<a href="/login">Add a user</a><br/>'
                ret += '<a href="/clean">Clean session</a><br/>'
                return ret
            return '<p>No active session<br /><a href="/login">Add a user</a></p>'

        @self.app.route("/test/<username>")
        def test(username):
            if 'username' in session:
                liste = json.loads(session['users'])
                print(liste)
                if liste is not None and username in liste:
                    session['username'] = escape(username)
                    return redirect("/")
            return redirect("/info")

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                session['username'] = request.form['username']
                if 'users' in session:
                    a = json.loads(session['users'])
                    if a is None:
                        a = []
                    a.append(request.form['username'])
                    session['users'] = json.dumps(a)
                else:
                    session['users'] = json.dumps([request.form['username']])

                return redirect("/info")
            return '''
                        <form method="post">
                            <p><input type=text name=username>
                            <p><input type=submit value=Login>
                        </form>
                    '''

        @self.app.route('/logout')
        def logout():
            session.pop('username', None)
            session.pop('users', None)
            return redirect("/info")

        @self.app.route('/clean')
        def clean():
            session.clear()
            return redirect("/info")

    def login_required(self, func):
        """Check if the user is connected"""

        def test(*args, **kwargs):
            try:
                if "username" not in session:
                    return redirect("/login")
                return func(*args, **kwargs)
            except Exception as e:
                return str(e), 500

        # Change the name of the function (for flask)
        test.__name__ = func.__name__
        return test

    def username(self):
        """
        Get the username of the client from session.

        This method is use by session manager or backend to get the username of the current client by using session
        """
        if "username" in session:
            return escape(session['username'])
        return redirect("/info")


    def route_add_session(self):
        """Will create a session"""
        try:
            backend = self.session_manager.add_session(self.username())
            return redirect(backend.url("/add_sessions/%s" % self.username()))
        except Exception:
            return redirect("/")
