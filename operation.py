#!/usr/bin/python
# coding:utf-8

import logging

from dbread import *
from modconf import *

a = getConfig('log')
logging.basicConfig(filename=a['logfile'], encoding="utf-8", filemode="a",
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.DEBUG)

def mergeproblem(originallist):
    """ 告警合并 """
    
    
    problemlist = []
    # normalist = []
    Unknown = []
    triggerkeylist = []
    sorts = []
    alarminfo = []

    # 判断告警or恢复,这里只处理告警状态的消息
    for origina in originallist:

        if origina['triggervalue'] == '1':
            problemlist.append(origina)
            if origina['triggerkey'] not in triggerkeylist:
                triggerkeylist.append(origina['triggerkey'])
        else:
            Unknown.append(origina)

    # 将不同triggerkey的报警放到List不同的下标里
    # 举例子: [[{A主机的SSH报警},{B主机的SSH报警}],[{A主机的ICMP报警},{B主机的ICMP报警}]]
    for triggerkey in triggerkeylist:
        for problem in problemlist:
            if problem['triggerkey'] == triggerkey:
                sorts.append(problem)
        alarminfo.append(sorts)
        sorts = []
    return alarminfo


def mergenormal(originallist):
    """ 恢复合并 """

    normallist = []
    Unknown = []
    triggerkeylist = []
    sorts = []
    alarminfo = []

    for origina in originallist:

        if origina['triggervalue'] == '0':
            normallist.append(origina)
            if origina['triggerkey'] not in triggerkeylist:
                triggerkeylist.append(origina['triggerkey'])
        else:
            Unknown.append(origina)

    for triggerkey in triggerkeylist:
        for normal in normallist:
            if normal['triggerkey'] == triggerkey:
                sorts.append(normal)
        alarminfo.append(sorts)
        sorts = []
    return alarminfo


def compressproblem(alarminfo):
    """ 告警压缩 """

    currenttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    messagelist = []
    for info in alarminfo:
        hostlist = []
        hostgroup = []
        eventidlist = []
        actionlist = []
        eventtime = info[0]['eventtime']
        triggerstatus = info[0]['triggerstatus']
        triggerseverity = info[0]['triggerseverity']
        triggername = info[0]['triggername']
        eventage = info[0]['eventage']
        itemvalue = info[0]['itemvalue']

        infonum = len(info)

        # 将主机分组
        for host in info:
            triggerkey = host['triggerkey']
            hostinfo = host['hostname']

            # 单主机有存在多组的情况,所以先切分后判断
            hostgrousplit = host['hostgroup'].split(', ')
            for group in hostgrousplit:
                if group not in hostgroup:
                    hostgroup.append(group)
            hostlist.append(hostinfo)
            # if host['hostgroup'] not in hostgroup:
            #     hostgroup.append(host['hostgroup'])
            # hostlist.append(hostinfo)

            # 获取eventid列表
            eventid = host['eventid']
            eventidlist.append(eventid)

            # 获取actions列表
            action = host['action']
            actionlist.append(action)

        # 根据eventidlist查询告警接收人和mediatypeid
        alert_receivera = alert_receiver(eventidlist, triggerkey)

        # 查询media_type然后定义告警信息及收件人/收件类型
        # EMAIL test@qq.com
        messageinfo = []

        # 查询所有的脚本名字和对应的mediatypeid
        media_type_list = mediatype()
        receiverlist = []
        receiverlisttwo = []

        # 将list处理为字符串-每个值之间增加逗号方便发送显示
        hoststr = ",".join(str(i) for i in hostlist)
        hostgroupstr = ",".join(str(i) for i in list(set(hostgroup)))
        actionstr = ",".join(str(i) for i in list(set(actionlist)))
        eventidstr = ",".join(str(i) for i in eventidlist)

        # 将两者融合得到结果:"通过什么脚本发送给谁"
        # 最终得到的结果: messagelist: [['告警脚本名字','收件人','告警信息主题','告警消息内容'],['告警脚本名字','收件人','告警信息主题','告警消息内容']]
        for a in media_type_list:
            for b in alert_receivera:
                if a[0] in b:
                    actions = a[1]
                    receiverlist.append(b[1])
                    continue

            messageinfo.append(actions)
            messageinfo.append(receiverlist)
            receiverlisttwo.append(receiverlist)
            receiverlist = []

            # 如果收件人为空则不执行下面的代码
            if (len(messageinfo[1])) == 0:
                continue

            if infonum == 1:
                if messageinfo[0] == 'SMS':
                    message = "故障%s:%s,%s在%s发生%s故障!\n详情见邮件" % (
                        triggerstatus, triggerseverity, hoststr, eventtime.split(' ')[1], triggername)
                    messageinfo.append(message)
                    messagelist.append(messageinfo)
                    messageinfo = []
                else:
                    subject = "故障%s,告警等级:%s,服务器:%s发生:%s故障!" % (triggerstatus, triggerseverity, hoststr, triggername)
                    message = "告警主机:%s\n告警等级:%s\n告警信息:%s\n告警项目:%s\n当前状态:%s " \
                              "%s\n故障持续:%s\n告警时间:%s\n分析时间:%s\n事件ID:%s\nActions:%s" % (
                                hoststr, triggerseverity, triggername, triggerkey, triggerstatus, itemvalue,
                                  eventage,
                                  eventtime,
                                  currenttime, eventidstr, actionstr)
                    messageinfo.append(subject)
                    messageinfo.append(message)
                    messagelist.append(messageinfo)
                    messageinfo = []

            elif infonum > 1:
                if messageinfo[0] == 'SMS':
                    message = "故障%s:%s服务器组:%s共%s台服务器在%s发生:%s故障!详情见邮件" % (
                        triggerstatus, triggerseverity, hostgroupstr, str(infonum), eventtime.split(' ')[1], triggername)
                    messageinfo.append(message)
                    messagelist.append(messageinfo)
                    messageinfo = []
                else:
                    subject = "故障%s,告警等级:%s服务器组:%s共%s台服务器发生:%s故障!" % (
                        triggerstatus, triggerseverity, hostgroupstr, str(infonum), triggername)
                    message = "共%s台服务器故障!\n涉及服务器组:%s\n涉及服务器:%s\n告警等级:%s\n告警信息:%s\n告警项目:%s\n当前状态:%s " \
                              "%s\n故障持续:%s\n告警时间:%s\n分析时间:%s\n事件ID:%s\nActions:%s" % (
                                  str(infonum), hostgroupstr, hoststr, triggerseverity, triggername, triggerkey,
                                  triggerstatus,
                                  itemvalue, eventage, eventtime, currenttime, eventidstr, actionstr)
                    messageinfo.append(subject)
                    messageinfo.append(message)
                    messagelist.append(messageinfo)
                    messageinfo = []

        # 将合并细节打印到日志中
        logging.info("Eventid:'%s', triggervalue:1, host:%s, triggerkey:'%s', actions:%s, receiverlist:%s" % (eventidstr, hoststr, triggerkey, actionstr, receiverlisttwo))
    return messagelist


def compressnormal(alarminfo):
    """ 恢复压缩 """

    currenttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    messagelist = []
    for info in alarminfo:
        hostlist = []
        hostgroup = []
        eventidlist = []
        actionlist = []
        triggerstatus = info[0]['triggerstatus']
        triggername = info[0]['triggername']
        eventage = info[0]['eventage']

        infonum = len(info)
        for host in info:
            triggerkey = host['triggerkey']
            hostinfo = host['hostname']
            if host['hostgroup'] not in hostgroup:
                hostgroup.append(host['hostgroup'])
            hostlist.append(hostinfo)

            eventid = host['eventid']
            eventidlist.append(eventid)

            action = host['action']
            actionlist.append(action)

        alert_receivera = alert_receiver(eventidlist, triggerkey)

        messageinfo = []
        media_type_list = mediatype()
        receiverlist = []
        receiverlisttwo = []

        hoststr = ",".join(str(i) for i in hostlist)
        hostgroupstr = ",".join(str(i) for i in list(set(hostgroup)))
        actionstr = ",".join(str(i) for i in list(set(actionlist)))
        eventidstr = ",".join(str(i) for i in eventidlist)

        for a in media_type_list:
            for b in alert_receivera:
                if a[0] in b:
                    actions = a[1]
                    receiverlist.append(b[1])
                    continue

            messageinfo.append(actions)
            messageinfo.append(receiverlist)
            receiverlisttwo.append(receiverlist)
            receiverlist = []

            if (len(messageinfo[1])) == 0:
                continue

            if infonum == 1:
                subject = "恢复%s,服务器:%s:%s已恢复! 故障持续%s" % (triggerstatus, hoststr, triggername, eventage)
                message = "恢复%s,服务器:%s:%s已恢复! 故障持续%s,分析时间:%s" % (
                    triggerstatus, hoststr, triggername, eventage, currenttime)
                messageinfo.append(subject)
                messageinfo.append(message)
                messagelist.append(messageinfo)
                messageinfo = []
            elif infonum > 1:
                subject = "恢复%s,服务器组:%s共%s台服务器%s已恢复! 故障持续%s" % (
                    triggerstatus, hostgroupstr, str(infonum), triggername, eventage)
                message = "恢复%s,服务器组:%s共%s台服务器%s已恢复! 故障持续%s,分析时间:%s" % (
                    triggerstatus, hostgroupstr, str(infonum), triggername, eventage, currenttime)
                messageinfo.append(subject)
                messageinfo.append(message)
                messagelist.append(messageinfo)
                messageinfo = []

        logging.info("Eventid:'%s', triggervalue:0, host:%s, triggerkey:'%s', actions:%s, receiverlist:%s" % (eventidstr, hoststr, triggerkey, actionstr, receiverlisttwo))
    return messagelist
