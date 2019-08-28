#!/usr/bin/env python
# coding:utf-8

import MySQLdb, sys, datetime, time
import redis

from dbread import *
from operation import *
from send_wechat import *
from send_email import *
from send_sms import *

sendtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

# 连接redis, 并读取所有事件id
subjectlist = get_redis()

# 从Mysqlalerts表获取报警的原始数据
originallist = []
for subject in subjectlist:
        a = alerts_eventid(subject)
        originallist.append(a)

# 将不同triggerkey的报警放到List不同的下标里
# 举例子: [[{A主机的SSH报警},{B主机的SSH报警}],[{A主机的ICMP报警},{B主机的ICMP报警}]]
problem = mergeproblem(originallist)
normal = mergenormal(originallist)

# 发送告警信息
# 将相同triggerkey的报警消息合并为一条并增加发送类型和收件人
# 举例子: [['告警脚本名字','收件人','主题:A+B主机的SSH报警','内容:A+B主机的SSH报警'],['告警脚本名字','收件人','主题:A+B主机的ICMP报警','内容:A+B主机的ICMP报警']]
messagelist = compressproblem(problem)

# 根据media_type定义的告警脚本名称分别发送给对应的人
if len(messagelist) != 0:
    for content in messagelist:
        if content[0] == 'WECHAT':
            tos = content[1]
            message = content[2] + '\n' + content[3]
            a = WeChat('https://qyapi.weixin.qq.com/cgi-bin')
            a.SendWechatMessage(tos, message)

        if content[0] == 'EMAIL':
            tos = content[1]
            subject = content[2]
            message = content[3]
            SendEmailMessage(tos, subject, message)

        if content[0] == 'SMS':
            tos = ",".join(str(i) for i in content[1])
            message = content[2]
            # SendSmsMessage(tos, message)

# 发送恢复信息
messagelist = compressnormal(normal)
if len(messagelist) != 0:
    for content in  messagelist:
        if content[0] == 'WECHAT':
            tos = content[1]
            message = content[3]
            a = WeChat('https://qyapi.weixin.qq.com/cgi-bin')
            a.SendWechatMessage(tos, message)

        if content[0] == 'EMAIL':
            tos = content[1]
            subject = content[2]
            message = content[3]
            SendEmailMessage(tos, subject, message)

        if content[0] == 'SMS':
            tos = ",".join(str(i) for i in content[1])
            message = content[2]
            # SendSmsMessage(tos, message)
