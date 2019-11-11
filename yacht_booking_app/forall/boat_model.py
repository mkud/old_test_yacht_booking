# -*- coding: utf-8 -*-
'''
Created on 8 jul 2017

@author: maxx
'''

class BoatModel(object):
    '''
    classdocs
    '''

    def __init__(self, id_operator, local_operator_id):
        '''
        Constructor
        '''
        self.id_operator = id_operator
        self.local_operator_id = local_operator_id
        self.parameters = {}
