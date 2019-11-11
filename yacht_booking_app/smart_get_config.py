# -*- coding: utf-8 -*-
'''
Created on 17 mar 2014

@author: Maxx
'''
import ConfigParser
import os

global_config = ConfigParser.RawConfigParser()
#if os.path.isfile('/management/HAP_Auth_Server/pysmart.ini'):
#    global_config.read('/management/HAP_Auth_Server/pysmart.ini')
#else:
#    global_config.read('pysmart.ini')
global_config.read(os.path.dirname(os.path.realpath(__file__)) + '/pysmart.ini')

