# collectd-yate
Collect yate statistics using collectd

## Requirements

- collectd
- python >= 2.3

## How to use

- copy collectd_yate.py to any directory e.g. /opt
- copy collectd_yate.conf to collectd.conf.d directory
- change  ModulePath "/opt" in collectd_yate.conf to reflect directory chosen
- change HOST + PORT in collectd_yate.conf to fit your yate config
- restart collectd to load new config