# -*- coding: utf-8 -*-
'''
Created on 8 jul 2017

@author: maxx
'''

from dateutil.relativedelta import relativedelta
import datetime

list_of_parameters = [ {"name": "source_place", "default": "Croatia", "from_text": lambda x: x, "to_text": lambda x: x}, 
                       {"name": "depart_date", "default": "", "from_text": lambda x: datetime.date.today() if x=="" else datetime.datetime.strptime(x, "%Y-%m-%d").date(), 
                                                                "to_text": lambda x: x.strftime("%Y-%m-%d")}, 
                       {"name": "count_week", "default": "1", "from_text": lambda x: int(x), "to_text": lambda x: str(x)}, 
                       {"name": "results_per_page", "default": "10", "from_text": lambda x: int(x), "to_text": lambda x: str(x)}, 
                       {"name": "current_page", "default": "1", "from_text": lambda x: int(x), "to_text": lambda x: str(x)}]

class SearchFilterParameters():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def InitFromRequest(self, request, database):
        for filter_param in list_of_parameters:
            self.__dict__[filter_param["name"]] = filter_param["from_text"](request.args.get(filter_param["name"], filter_param["default"]))
        self.FetchIDsForPlaces(database)
        
    def PutToGetString(self):
        return "&".join([x["name"] + "=" + x["to_text"](self.__dict__[x["name"]]) for x in list_of_parameters])

    def PutToGetStringWithNewNumPage(self, new_num_page):
        return "&".join(["current_page=" + str(new_num_page) if (x["name"] == "current_page") else (x["name"] + "=" + x["to_text"](self.__dict__[x["name"]]))  
                                    for x in list_of_parameters])
    
    def GetDepartDate(self, weekday=5):
        '''
        Get current date and align to saturday 
        '''
        if weekday >= self.depart_date.weekday():
            add_date = weekday - self.depart_date.weekday()
        else:
            add_date = 7 + weekday - self.depart_date.weekday()
        return self.depart_date + relativedelta(days=add_date)    
        
    def GetFinishDate(self, weekday=5):
        return self.GetDepartDate(weekday) + relativedelta(days=7)
    
    def FetchIDsForPlaces(self, database_conn):
        self.IDsForPlaces = {} 
        # key - operator_id ; value - level+id
        infos_from_db = database_conn.Site_GetOnePlace(self.source_place)
        for one_val in infos_from_db:
            if one_val[0] not in self.IDsForPlaces or self.IDsForPlaces[one_val[0]]["level"] > one_val[2]:
                self.IDsForPlaces[one_val[0]] = {"level":one_val[2], "id": one_val[1]}
    
        