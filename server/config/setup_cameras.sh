#!/usr/bin/env bash

apt-get install -y -q crtmpserver 
apt-get install -y -q supervisor 

patch /etc/init.d/supervisor < supervisor.patch

ln -s /opt/elixys/config/elixyssupervisord.conf  \ 
        /etc/supervisor/conf.d

service crtmpserver restart
service supervisor restart
