#!/usr/bin/env python
# coding:utf-8

import sys
import redis

from dbread import *
from operation import *


# 连接redis, 并读取所有事件id
subjectlist = get_redis()

# 从Mysql alerts表获取报警的原始数据
originallist = []
for subject in subjectlist:
        a = alerts_eventid(subject)
        originallist.append(a)

# 告警信息合并
problem = mergeproblem(originallist)
# 恢复信息合并
normal = mergenormal(originallist)


# 告警信息压缩
messagelist = compressproblem(problem)
# 发送告警信息
sendalarmmessage(messagelist)

# 恢复信息压缩
messagelist = compressnormal(normal)
# 发送恢复信息
sendalarmmessage(messagelist)
