# -*- coding: utf-8 -*-
'''
Created on 6 jul 2017

@author: maxx

Contain API for working with Sedna operator
http://www.sednasystem.io/

'''

import lxml.etree

import forall.operator
import forall.places
import forall.fleet_operator
import forall.boat
import forall.boat_model

# Contains the dependency tree of regions
LEVELS_SEDNA = {"destination": {"level": 1, "parent": "global_parent", "parent_level": 0, "id_name": "id_dest"},
          "country": {"level": 2, "parent": "destination", "parent_level": 1, "id_name": "id_country"},
          "base": {"level": 3, "parent": "country", "parent_level": 2, "id_name": "id_base"},
          "marina": {"level": 4, "parent": "base", "parent_level": 3, "id_name": "id_marina"}}
LEVELS_FOR_SEARCH = {1: "d", 2: "c"}

# internal system id of Sedna operator
OPERATOR_ID_SEDNA = 1
# Login for access to Sedna system
SEDNA_CLIENT_ID = 7219

# Dictionary of image types
TYPE_PICTS = {"picts": 1, "plans": 2}

class OperatorSedna(forall.operator.OperatorApi):
    '''
    This class encapsulates the API for working with Sedna. 
    Must contain the same methods as the other classes in this package
    '''

    def __init__(self):
        '''
        Constructor
        I made base class, but it isn't used
        '''
        super(OperatorSedna, self).__init__(OPERATOR_ID_SEDNA)
    
    def GetPlaces(self):
        '''
        Gets all the home points for this operator (countries, ports, ...)
        Used 1 time in year (or some month) by syncer.py
        '''
        # get information from service and parce it
        d = lxml.etree.parse("http://client.sednasystem.com/API/GetDestinations3.asp?lg=0&refagt=dghs{}".format(SEDNA_CLIENT_ID))
        iterator_places = d.iter()

        
        # this dictionary was used for making tree structure in database. 
        ids = {"global_parent": 0, "destination": 0, "country": 0, "base": 0, "marina": 0}
        
        # return results
        result = []
        
        # append new place to results 
        for place in iterator_places:
            if place.tag in ids:
                ids[place.tag] = place.get(LEVELS_SEDNA[place.tag]["id_name"])
                result.append(forall.places.PlaceEntity(LEVELS_SEDNA[place.tag]["level"],
                                                        ids[place.tag],
                                                        place.get("name"),
                                                        ids[LEVELS_SEDNA[place.tag]["parent"]],
                                                        LEVELS_SEDNA[place.tag]["parent_level"]))
        return result

    def GetFleetOperators(self):
        '''
        Get all possible charter companies and result as list of forall.fleet_operator.FleetOperator
        Used 1 time in year (or some month) by syncer.py
        '''

        # get information from service and parce it
        d = lxml.etree.parse("http://client.sednasystem.com/API/getOperators.asp?refagt=dghs{}".format(SEDNA_CLIENT_ID))
        operators = d.getroot()

        # return results
        result = []
        
        # For all selected operators
        for operator in operators:
            cur_operator = forall.fleet_operator.FleetOperator(OPERATOR_ID_SEDNA, operator.get("id_ope"))
            for key, value in operator.attrib.iteritems():
                cur_operator.parameters[key] = value
            for child in operator:
                if child.tag == "bankinfo":
                    cur_operator.parameters["bankinfo"] = child.text[0:127]
                    break
            # append to results list
            result.append(cur_operator)
        return result
        

    def GetEquipmentAndCategory(self):
        '''
        Ask dictionary with possible additional equipment and equipment category from operator 
        Used 1 time in year (or some month) by syncer.py
        '''

        # get information from service and parce it
        d = lxml.etree.parse("http://client.sednasystem.com/API/getExtrasCharFleet.asp?refagt=dghs{}&typ=char".format(SEDNA_CLIENT_ID))
        equipments = d.getroot()

        # result of this fuction is 2 lists
        result = {"equipment": [], "category":[]}
        for equipment in equipments:
            result["equipment"].append({"id": equipment.get("id_opt"), "name": equipment.text.strip(), "categoryId": None})
       
        # for this operator equipment's category not implemented 
        return result

    def SearchBoat(self, filter_params):
        '''
        Run every time we need find boat. Not for syncing, only for service 
        '''
        # !!!!Period should be aligned to saturday - global yacht booking standart
        depart_date = filter_params.GetDepartDate()
        if filter_params.IDsForPlaces[OPERATOR_ID_SEDNA]["level"] not in LEVELS_FOR_SEARCH:
            return forall.search_result.SearchResult(id_operator=self.operator_id,
                                                   total_count=0,
                                                   total_pages=0)
        
        # Exceptions was used, because search result can be empty with hi possibility 
        try:
            # get information from service and parce it
            d = lxml.etree.parse("http://client.sednasystem.com/m3/agt/{0}/default.api.asp?action=search&srh_dest={1}{2}&DEPART_DD={3:0>2}&DEPART_MM={4:0>2}&DEPART_YYYY={5}&nombjour={6}&Xml_light=1&Offset={7}&Limit={8}".format(SEDNA_CLIENT_ID,
                                                                                                                                                                                    LEVELS_FOR_SEARCH[filter_params.IDsForPlaces[OPERATOR_ID_SEDNA]["level"]],
                                                                                                                                                                                    filter_params.IDsForPlaces[OPERATOR_ID_SEDNA]["id"],
                                                                                                                                                                                    depart_date.day,
                                                                                                                                                                                    depart_date.month,
                                                                                                                                                                                    depart_date.year,
                                                                                                                                                                                    filter_params.count_week * 7,
                                                                                                                                                                                    (filter_params.current_page-1) * filter_params.results_per_page,
                                                                                                                                                                                    filter_params.results_per_page))
        
            list_of_boats = d.getroot()
            
            result = forall.search_result.SearchResult(id_operator=self.operator_id,
                                               total_count=((filter_params.results_per_page * (filter_params.current_page-1) + len(list_of_boats)) 
                                                        if (len(list_of_boats) < filter_params.results_per_page)
                                                        else filter_params.results_per_page * filter_params.current_page + 1)
                                                        if len(list_of_boats) else 0,
                                               total_pages=filter_params.current_page 
                                                        if (len(list_of_boats) < filter_params.results_per_page)
                                                        else filter_params.current_page + 1)
        
            for one_boat in list_of_boats:
                result.AppendBoatFromSearch(boat_id=int(one_boat.get("id_boat")),
                                            price_for_client=int(one_boat.get("newprice")),
                                            price_by_pricelist=int(one_boat.get("oldprice")),
                                            discounts_in_procent=int(one_boat.get("discount")))
            return result
        except:
            return forall.search_result.SearchResult(id_operator=self.operator_id,
                                                   total_count=0,
                                                   total_pages=0)
            
    def CheckBoatFree(self, filter_params_one_boat):
        '''
        Check if one founded boat is available for booking 
        Lask check before booking 
        '''
        # !!!!Period should be aligned to saturday - global yacht booking standart
        depart_date = filter_params_one_boat.GetDepartDate()
        if filter_params_one_boat.id_operator <> OPERATOR_ID_SEDNA:
            return forall.search_result.SearchResult(id_operator=self.operator_id,
                                                   total_count=0,
                                                   total_pages=0)

        # Exceptions was used, because search result can be empty with hi possibility 
        try:
            # get information from service and parce it
            d = lxml.etree.parse("http://client.sednasystem.com/m3/agt/{0}/default.api.asp?action=search&DEPART_DD={1:0>2}&DEPART_MM={2:0>2}&DEPART_YYYY={3}&nombjour={4}&id_boat={5}&dis_option=0&Xml_light=1".format(SEDNA_CLIENT_ID,
                                                                                                                                                                                    depart_date.day,
                                                                                                                                                                                    depart_date.month,
                                                                                                                                                                                    depart_date.year,
                                                                                                                                                                                    filter_params_one_boat.count_week * 7,
                                                                                                                                                                                    filter_params_one_boat.id_boat))
        
            list_of_boats = d.getroot()
            
            result = forall.search_result.SearchResult(id_operator=self.operator_id,
                                               total_count=len(list_of_boats),
                                               total_pages=len(list_of_boats))
        
            for one_boat in list_of_boats:
                result.AppendBoatFromSearch(boat_id=int(one_boat.get("id_boat")),
                                            price_for_client=int(one_boat.get("newprice")),
                                            price_by_pricelist=int(one_boat.get("oldprice")),
                                            discounts_in_procent=int(one_boat.get("discount")))
            return result
        except:
            return forall.search_result.SearchResult(id_operator=self.operator_id,
                                                   total_count=0,
                                                   total_pages=0)


    def GetBoats(self, charters_company_ids):
        '''
        Used 1 time in year (or some month) by syncer.py
        '''
        result = []
        for charters_company_id in charters_company_ids:
            # get information from service and parce it
            d = lxml.etree.parse("http://client.sednasystem.com/API/getBts4.asp?refagt=dghs{0}&id_ope={1}".format(SEDNA_CLIENT_ID, charters_company_id))
            boats = d.getroot()
            for boat in boats:
                cur_boat = forall.boat.Boat(OPERATOR_ID_SEDNA, boat.get("id_boat"), boat.get("id_model"))
                for key, value in boat.attrib.iteritems():
                    cur_boat.parameters[key] = value.encode("utf-8")[0:127]

                
                for element in boat:
                    if element.tag in TYPE_PICTS:
                        # Append images
                        for one_pict in element:
                            cur_boat.images.append({"url":one_pict.get("link"), "type": TYPE_PICTS[element.tag]})
                    elif element.tag == 'characteristics':
                        # Append additional equipment
                        for characteristic_topic in element:
                            cur_group = characteristic_topic.get("topic").strip()
                            for characteristic in characteristic_topic:
                                cur_boat.equipment.append({"id": characteristic.get("id_opt").strip(),
                                                           "value": characteristic.get("quantity").strip(),
                                                           "unit":characteristic.get("unit").strip(),
                                                           "name_group": cur_group,
                                                           "comment": ""})
                    elif element.tag == 'homeport':
                        # append base ports
                        cur_boat.ports.append({"id_place": element.get("id_base"), "level": LEVELS_SEDNA["base"]["level"], "id_type":1})
                        # cur_boat.ports.append({"id_place": element.get("id_country"), "level": LEVELS_SEDNA["country"]["level"], "id_type":1}) 
                        
                result.append(cur_boat)
                    
        return result
        
    def GetBoatModels(self):
        '''
        Get all available yachts models from operator
        Used 1 time in year (or some month) by syncer.py
        '''
        result = []
        # get information from service and parce it
        d = lxml.etree.parse("http://client.sednasystem.com/API/GetBt_model.asp?refagt=dghs{0}".format(SEDNA_CLIENT_ID))
        models = d.getroot()
        
        for model in models:
            cur_model = forall.boat_model.BoatModel(OPERATOR_ID_SEDNA, model.get("id_model"))
            for key, value in model.attrib.iteritems():
                cur_model.parameters[key] = value.encode("utf-8")[0:127]
            result.append(cur_model)
        return result

    def BookYacht(self, UserInfo, date_from, date_to, yacht_id):
        '''
        Not yet implemented
        '''
        pass

if __name__ == '__main__':
    '''
    This is testing func for debug
    '''
    oper = OperatorSedna()
    charters_company_ids = [x.local_operator_id for x in oper.GetFleetOperators()]
    res = oper.GetBoats(charters_company_ids)
    
