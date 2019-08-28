#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib,urllib2,json
import sys
from modconf import *

reload(sys)
sys.setdefaultencoding( "utf-8" )

class WeChat(object):
        __token_id = ''
        # init attribute
        def __init__(self,url):
                a = getConfig('wechat')
                self.__url = url.rstrip('/')
                self.__corpid = a['wechatcorpid']
                self.__secret = a['wechatsecret']

        # Get TokenID
        def authID(self):
                params = {'corpid':self.__corpid, 'corpsecret':self.__secret}
                data = urllib.urlencode(params)

                content = self.getToken(data)

                try:
                        self.__token_id = content['access_token']
                        # print content['access_token']
                except KeyError:
                        raise KeyError

        # Establish a connection
        def getToken(self,data,url_prefix='/'):
                url = self.__url + url_prefix + 'gettoken?'
                try:
                        response = urllib2.Request(url + data)
                except KeyError:
                        raise KeyError
                result = urllib2.urlopen(response)
                content = json.loads(result.read())
                return content

        # Get sendmessage url
        def postData(self,data,url_prefix='/'):
                url = self.__url + url_prefix + 'message/send?access_token=%s' % self.__token_id
                request = urllib2.Request(url,data)
                try:
                        result = urllib2.urlopen(request)
                except urllib2.HTTPError as e:
                        if hasattr(e,'reason'):
                                print 'reason',e.reason
                        elif hasattr(e,'code'):
                                print 'code',e.code
                        return 0
                else:
                        content = json.loads(result.read())
                        result.close()
                return content

        # send message
        def SendWechatMessage(self,touser,message):

                self.authID()
                a = getConfig('wechat')

                data = json.dumps({
                        'touser':touser,
                        'toparty':"1",
                        'msgtype':"text",
                        'agentid':a['wechatagentid'],
                        'text':{
                                'content':message
                        },
                        'safe':"0"
                },ensure_ascii=False)

                response = self.postData(data)
                print response


if __name__ == '__main__':
        a = WeChat('https://qyapi.weixin.qq.com/cgi-bin')
        a.SendWechatMessage(sys.argv[1],sys.argv[3])