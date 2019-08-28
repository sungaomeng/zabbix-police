#!/usr/bin/env python
# coding:utf-8

# Desc: 短信http接口的python代码调用示例
# https://www.yunpian.com/api/demo.html
# https访问，需要安装  openssl-devel库。apt-get install openssl-devel

import httplib
import urllib
import json, sys
from modconf import *

# 服务地址
sms_host = "sms.yunpian.com"
# 端口号
port = 443
# 版本号
version = "v2"
# 智能匹配模板单条发送短信接口的URI
#sms_send_uri = "/" + version + "/sms/single_send.json"

# 智能匹配模板批量发送短信接口的URI
sms_send_uri = "/" + version + "/sms/batch_send.json"

# 修改为您的apikey.可在官网（http://www.yunpian.com)登录后获取
a = getConfig('sms')
apikey = a['smsapikey']

# 修改为短信的签名
tpl = "【roobo】监控告警： "

def SendSmsMessage(mobile, text):
    """
    通用接口发短信
    """

    params = urllib.urlencode({'apikey': apikey, 'text': tpl+text, 'mobile':mobile})
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"
    }
    conn = httplib.HTTPSConnection(sms_host, port=port, timeout=30)
    conn.request("POST", sms_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'invalidate arguments'
        print 'eg: python send_sms.py mobile msgcontent'
        exit(1)

    # 修改为您要发送的手机号码
    mobile = sys.argv[1]

    # 短信内容
    text = sys.argv[2]

    # 调用智能匹配模板接口发短信
    print SendSmsMessage(mobile, text)
