# -*- coding: utf-8 -*-
'''
Created on 7 jul 2017

@author: maxx
'''

class PlaceEntity():
    '''
    classdocs
    '''

    def __init__(self, level, local_operator_id, name, local_operator_parent_id, parent_level, code="", lat=0, lon=0, global_id=0):
        '''
        Constructor
        '''
        self.local_operator_id = local_operator_id
        self.name = name 
        self.level = level 
        self.local_operator_parent_id = local_operator_parent_id
        self.global_id = global_id
        self.parent_level = parent_level
        self.code = code
        self.lat = lat
        self.lon = lon
