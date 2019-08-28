#!/usr/bin/python
# coding:utf-8

import ConfigParser, os


def getConfig(sections):
    config = ConfigParser.ConfigParser()
    path = os.path.split(os.path.realpath(__file__))[0] + '/police.conf'
    config.read(path)

    ConfigDict = {}

    for item in config.items(sections):
        key = sections+item[0]
        vaule = item[1]
        ConfigDict[key] = vaule

    return ConfigDict
