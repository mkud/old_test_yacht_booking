# -*- coding: utf-8 -*-
'''
Created on 8 jul 2017

@author: maxx
'''

class Boat(object):
    '''
    classdocs
    '''

    def __init__(self, id_operator, local_operator_id, boat_model):
        '''
        Constructor
        '''
        self.id_operator = id_operator
        self.local_operator_id = local_operator_id
        self.boat_model = boat_model
        self.parameters = {}
        self.images = []
        self.equipment = []
        self.ports = []