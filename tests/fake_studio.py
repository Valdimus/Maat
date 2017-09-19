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

import subprocess
import pwd
import os
import copy


class FakeStudio:
    """Juste a way to create a fake rstudio"""

    def __init__(self, command):
        """
        :param command: Command to use to launch a fake rsession
        """
        self.__command = command
        self.__users = {}

    def __del__(self):
        # Stop all client
        self.stop_all()
        del self.__users

    @property
    def command(self):
        return self.__command

    @property
    def users(self):
        return self.__users

    def client_running(self, username):
        """
        Check if a client have a running session
        :param username:
        :return: boolean
        """
        if username in self.users.keys():
            if len(self.users[username]) == 0:
                return False
            a = self.users[username][-1].poll()
            if a is not None:
                # self.users[username].pop()
                return False
            return True
        return False

    def spawn_client(self, username):
        """
        Spawn a client for an user
        :param username:
        :return:
        """

        # if self.client_running(username):
        #     return True

        try:
            def demote(user_uid, user_gid):
                def result():
                    os.setgid(user_gid)
                    os.setuid(user_uid)
                return result

            # http://stackoverflow.com/questions/1770209/run-child-processes-as-different-user-from-a-long-running-process/6037494#6037494
            pw_record = pwd.getpwnam(username)
            user_name = pw_record.pw_name
            user_home_dir = pw_record.pw_dir
            user_uid = pw_record.pw_uid
            user_gid = pw_record.pw_gid
            env = os.environ.copy()
            env['HOME'] = user_home_dir
            env['LOGNAME'] = user_name
            env['PWD'] = os.getcwd()
            env['USER'] = user_name
            if username not in self.users:
                self.users[username] = []
            self.users[username].append(subprocess.Popen(
                [self.command], preexec_fn=demote(user_uid, user_gid), cwd=os.getcwd(), env=env
            ))
            return True
        except Exception as e:
            print(str(e))
            return False

    def stop_all(self):
        for i in self.__users.keys():
            self.stop_client(i, no_pop=True)

    def stop_client(self, username, no_pop=False):
        """
        Stop all session of a client
        :param username:
        :param no_pop: Don't pop the username
        :return:
        """
        if self.client_running(username):
            self.users[username][-1].kill()
            self.users[username][-1].wait(0.1)
            self.users[username].pop()
            if len(self.users[username]) == 0 and not no_pop:
                self.users.pop(username)
