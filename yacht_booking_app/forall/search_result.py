# -*- coding: utf-8 -*-
'''
Created on 17 jul 2017

@author: maxx
'''

import boat_from_db

class SearchResult(object):
    '''
    classdocs
    '''


    def __init__(self, id_operator, total_count=None, total_pages=None):
        '''
        Constructor
        '''
        self.id_operator = id_operator
        self.boats_sorted = []
        self.boats = {}
        self.total_count = total_count
        self.total_pages = total_pages
    
    def AppendBoatFromSearch(self, boat_id, price_for_client, price_by_pricelist=None, discounts_in_procent=None):
        one_boat = boat_from_db.BoatFromDB(self.id_operator, boat_id, price_by_pricelist, price_for_client, discounts_in_procent)
        self.boats_sorted.append(one_boat)
        self.boats[boat_id] = one_boat

    def InitFromDatabase(self, data_base):
        all_boats_ids = ",".join(map(str, self.boats.keys()))
        result_from_db = data_base.Site_GetManyBoats(self.id_operator, all_boats_ids)

        for one_param in result_from_db:
            if one_param[1] is not None and one_param[2] is not None:
                self.boats[one_param[0]].AppendParamFromDB(one_param[1], one_param[2])

    def GetCountBoats(self):
        return len(self.boats)
    
    def TrimToSize(self, wish_size):
        while len(self.boats) > wish_size:
            del self.boats[self.boats_sorted.pop().local_operator_id]
        
    def Merge(self, another_results):
        self.total_count += another_results.total_count
        self.total_pages = max(self.total_pages, another_results.total_pages)
        self.boats_sorted += another_results.boats_sorted
        