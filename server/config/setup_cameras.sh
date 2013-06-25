#!/usr/bin/env bash

sudo apt-get install -y -q crtmpserver 
sudo apt-get install -y -q supervisor 

sudo ln -s /opt/elixys/config/elixyssupervisord.conf  \ 
        /etc/supervisor/conf.d/

sudo service crtmpserver restart
sudo service supervisor restart
