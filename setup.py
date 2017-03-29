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
# Date: 28/03/2017

from setuptools import setup, find_packages

print(find_packages())
# Merci Sam & Max : http://sametmax.com/creer-un-setup-py-et-mettre-sa-bibliotheque-python-en-ligne-sur-pypi/

setup(
    name='maat',
    version="0.1.0",
    packages=find_packages(),
    author="Christophe NOUCHET",
    author_email="nouchet.christophe@gmail.com",
    description="Maât",
    long_description="Just a basic session manager / load balancer",
    install_requires=[
        "flask",
        "psutil",
        "gevent",
        "requests"
    ],
    # Active la prise en compte du fichier MANIFEST.in
    include_package_data=False,
    url='',

    entry_points={
        'console_scripts': [
            'maat-agent = maat.agent:main']
    },
    scripts=[],

    license="GPL3",
)

