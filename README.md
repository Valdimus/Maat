# Maât

<a title="By No machine-readable author provided. Jeff Dahl assumed (based on copyright claims). [GFDL (http://www.gnu.org/copyleft/fdl.html) or CC BY-SA 4.0-3.0-2.5-2.0-1.0 (http://creativecommons.org/licenses/by-sa/4.0-3.0-2.5-2.0-1.0)], via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File%3AMaat.svg"><img width="256" alt="Maat" src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Maat.svg/256px-Maat.svg.png"/></a>


## Information

This project can be use to load balance user between some backends, so you can make a cluster of this backend. I start this project to load balance users between multiple instance of Rstudio without the Pro version of Rstudio (because I am poor T.T). So I want to make a Rstudio cluster.


The way that Rstudio work is pretty simple. For each user, it will create an process with the name 'rsession', so if you can simply watch process you can know:

* witch user is connected to Rstudio
* How manny resources he is consuming (cpu percent, memory percent)
* On witch project is he working on (because Rstudio project are just directory, and with the current_working_directory (cwd) of the process we know it)


So the principal of this project is to detect witch backend (Rstudio server) have the less user conencted to it to create a session for a new user or eaven handle multiple sessions on different backend. For this purpose you have to launch a MaatAgent on this backend.

A MaatAgent is just the program that will watch 'rssession' process for each user and expose it on a HTTP API. It will also, register when a user want to create a sessions on the Rstudio service when we are doing the loadbalance (the time that the user really create the session aka connected to Rstudion, otherwise if all user arrive at the same time, the load balancer will choose the same backend for all user)

The second part of this project is the loadbalancer istance. It is a HTTP website that will list all available backend (Rstudio server) and choose the correct one for each user. It don't store anything on this part of the project. Only use HTTP API of the MaatAgent (and cache on it) to make his decision. So you can have as many loadbalancer as you want.


## Summary

This project will help you to:
* Make a cluster of Rstudio
* Have multiple session for an user on multiple server (1 session by Rstudio server for an user)

## License

Copyright (C) 2017 NOUCHET Christophe


This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or at your option) any later version.


This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.


You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.


## TODO

* Clearify the api and architecture of the project
* Add more test on the loadbalancer
* Create a locakable website for the loadbalancer