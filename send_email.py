#!/usr/bin/python
# encoding:utf-8
# filename: mail.py

import smtplib
from email.mime.text import MIMEText
from modconf import *
import time, sys


def email(HOST, PORT, FROM, PASSWORD, TOs, SUBJECT, BODY):
    msg = MIMEText(BODY, 'plain', _charset='UTF-8')
    msg['To'] = ', '.join(TOs)
    msg['From'] = FROM
    msg['Subject'] = SUBJECT
    content = []
    content.append('From: ' + FROM)
    content.append('To: ' + ', '.join(TOs))
    content.append('Subject: ' + SUBJECT)
    content.append('')
    content.append(BODY)
    data = '\r\n'.join(content)
    data = msg.as_string()

    server = smtplib.SMTP_SSL()
    server.connect(HOST, PORT)
    # server.starttls()
    server.login(FROM, PASSWORD)
    server.sendmail(FROM, TOs, data)
    server.quit()


def SendEmailMessage(touser, subject, message):
    """ 发送邮件消息 """


    a = getConfig('email')
    email(a['emailhost'], a['emailport'],a['emailuser'], a['emailpassword'], touser, subject, message)

    # 如果单个邮箱发送比较慢的话可以使用多个邮箱发送邮件
    # t = int(time.time() * 1000)
    # if t%3 ==0:
    #     email(a['emailhost'], a['emailport'],a['emailuser'], a['emailpassword'], touser, subject, message)
    # elif t%3 ==1:
    #     email(a['emailhost'], a['emailport'],a['emailuser'], a['emailpassword'], touser, subject, message)
    # else:
    #     email(a['emailhost'], a['emailport'],a['emailuser'], a['emailpassword'], touser, subject, message)

    print 'done'



if __name__ == "__main__":
    if len(sys.argv) != 4:
        print 'aaa',sys.argv
        print 'invalidate arguments'
        print 'eg: zabbix@roobo.com title msgcontent'
        exit(1)
    SendEmailMessage(sys.argv[1], sys.argv[2], sys.argv[3])