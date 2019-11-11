# -*- coding: utf-8 -*-
'''
Created on 18 jul 2017

@author: maxx
'''

# Dictionary of available types of boat images
PHOTOS_LEVELS = {'Main Photo':1, 'Photo':2, 'Ext Photo':3}

class BoatFromDB(object):
    '''
    classdocs
    '''


    def __init__(self, id_operator, local_operator_id, price_from_pricelist = None, price_for_client = None, discount = None):
        '''
        Constructor
        '''
        self.params = {}
        self.pictures = []
        self.id_operator = id_operator
        self.local_operator_id = local_operator_id
        self.main_picture = ""
        self.main_picture_level = 100
        
        self.price_from_pricelist = price_from_pricelist
        self.price_for_client = price_for_client
        self.discount = int(discount)
        
    def AppendParamFromDB(self, name, value):
        if name in PHOTOS_LEVELS:
            self.pictures.append(value)
            if self.main_picture_level > PHOTOS_LEVELS[name]:
                self.main_picture = value
                self.main_picture_level = PHOTOS_LEVELS[name]
        else:
            self.params[name] = value
