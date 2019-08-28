#!/usr/bin/env python
# coding:utf-8

import redis
import sys
from modconf import *

a = getConfig('redis')
if len(a['redispassword']) == 0:
    r = redis.StrictRedis(host=a['redishost'], port=a['redisport'])
else:
    r = redis.StrictRedis(host=a['redishost'], port=a['redisport'], db='a[redisdb]', password=a['redispassword'])

subject = sys.argv[1]
r.set(subject, subject)
