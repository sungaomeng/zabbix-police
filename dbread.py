#!/usr/bin/python
# coding:utf-8
# 脚本中*****需要修改的地方

import MySQLdb, redis
import datetime, time, sys
from modconf import *


def alerts_eventid(event_id):
    """定义通过subject获取数据库告警具体信息,并以字典形式返回,每个EventID仅返回一条action信息"""


    a = getConfig('mysql')
    try:
        conn = MySQLdb.connect(host=a['mysqlhost'], user=a['mysqluser'], passwd=a['mysqlpassword'], db=a['mysqldb'], port=int(a['mysqlport']))
        cursor = conn.cursor()
        cursor.execute("SET NAMES utf8");
        # sql = "SELECT * FROM alerts where eventid = '%s' ;" % (event_id)
        # 这里由eventid改为subject的原因是:如果报警瞬间恢复,这个程序同时处理报警和恢复则会将恢复消息也合并到报警信息里
        # mysql插入的恢复和报警的eventid是不同的,但action在写入redis时的actionid是相同的,所以查询会重复,导致上面说的问题
        sql = "SELECT * FROM alerts where subject = '%s' ;" % (event_id)
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        # 相同的eventid只取一条
        event = data[0]
        messagelist = []
        # 只获取subject列的数据
        message = event[8]
        # 以"\r\n"为间隔切分数据
        messageone = message.split('\r\n')
        for i in messageone:
            # 以|为分隔符切分keyvaule
            messagelist.append(i.split('|'))
        messagedict = dict(messagelist)
        return messagedict
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def mediatype():
    """查询mediatypeid对应的脚本"""

    a = getConfig('mysql')
    try:
        conn = MySQLdb.connect(host=a['mysqlhost'], user=a['mysqluser'], passwd=a['mysqlpassword'], db=a['mysqldb'], port=int(a['mysqlport']))
        cursor = conn.cursor()
        cursor.execute("SET NAMES utf8");
        sql = "SELECT mediatypeid,description FROM media_type;"
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def alerts_sedto(event_id):
    """查询收件人"""

    a = getConfig('mysql')
    try:
        conn = MySQLdb.connect(host=a['mysqlhost'], user=a['mysqluser'], passwd=a['mysqlpassword'], db=a['mysqldb'], port=int(a['mysqlport']))
        cursor = conn.cursor()
        cursor.execute("SET NAMES utf8");
        sql = "SELECT * FROM alerts where subject in '%s' ;" % (event_id)
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def alert_receiver(event_id, triggerkey):
    """ 查询告警接收人 """


    a = getConfig('mysql')
    try:
        conn = MySQLdb.connect(host=a['mysqlhost'], user=a['mysqluser'], passwd=a['mysqlpassword'], db=a['mysqldb'], port=int(a['mysqlport']))
        cursor = conn.cursor()
        cursor.execute("SET NAMES utf8");
        sql = "SELECT distinct mediatypeid,sendto FROM alerts where subject in (%s) and message like '%%%s%%' ;" % (
            (','.join(event_id)), triggerkey)
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

def get_redis():
    """ 连接redis, 并读取所有事件id """


    a = getConfig('redis')
    if len(a['redispassword']) == 0:
        r = redis.StrictRedis(host=a['redishost'], port=a['redisport'])
    else:
        r = redis.StrictRedis(host=a['redishost'], port=a['redisport'], db='a[redisdb]', password=a['redispassword'])

    eventidlist = r.keys()
    for i in eventidlist:
        print "redis keys = ", i
        # r.delete(i)
        # r.flushdb()

    return eventidlist