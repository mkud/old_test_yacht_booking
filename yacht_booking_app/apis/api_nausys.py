# -*- coding: utf-8 -*-
'''
Created on 6 jul 2017

@author: maxx

Contain API for working with Nausys operator
http://www.nausys.com/en/

'''

import cjson
import requests
import datetime

import forall.operator
import forall.places
import forall.fleet_operator
import forall.boat
import forall.boat_model
import forall.search_filter
import forall.search_result

# Contains the dependency tree of regions
LEVELS_NAUSYS = {"countries": {"level": 2, "parent_level": 0, "parent": "none"},
                 "regions": {"level": 3, "parent_level": 2, "parent": "countryId"},
                 "locations": {"level": 4, "parent_level": 3, "parent": "regionId"}}
LIST_PLACES_TYPE = ['countries', 'regions', 'locations']
LEVELS_NAUSYS2 = {2:'countries', 3:'regions', 4:'locations'}

# internal system id of Nausys operator 
OPERATOR_ID_NAUSYS = 2

# Login for access to Nausys system
USER_NAME_NAUSYS = "zzz"
PASSWORD_NAUSYS = "zzz"

class OperatorNausys(forall.operator.OperatorApi):
    '''
    This class encapsulates the API for working with Nausys. 
    Must contain the same methods as the other classes in this package
    '''

    def __init__(self):
        '''
        Constructor
        I made base class, but it isn't used
        '''
        super(OperatorNausys, self).__init__(OPERATOR_ID_NAUSYS)
    
    def GetPlaces(self):
        '''
        Gets all the home points for this operator (countries, ports, ...)
        Used 1 time in year (or some month) by syncer.py
        '''
        result = []
        
        # Make a request to the system for each type
        for cur_place_type in LIST_PLACES_TYPE:
            # get information from service and parce it
            r = requests.post("http://ws.nausys.com/CBMS-external/rest/catalogue/v6/{}".format(cur_place_type), data='{{"username":"{0}", "password":"{1}"}}'.format(USER_NAME_NAUSYS, PASSWORD_NAUSYS), headers={'content-type': 'application/json'})
            result_as_obj = cjson.decode(r.text)
            
            # And append to return results all returned places 
            for place in result_as_obj[cur_place_type]:
                result.append(forall.places.PlaceEntity(LEVELS_NAUSYS[cur_place_type]["level"],
                                                        place["id"],
                                                        place["name"]["textEN"],
                                                        place.get(LEVELS_NAUSYS[cur_place_type]["parent"], 0),
                                                        LEVELS_NAUSYS[cur_place_type]["parent_level"],
                                                        place.get("code", ""),
                                                        place.get("lat", 0),
                                                        place.get("lon", 0)
                                                        ))
        return result
    
    def GetFleetOperators(self):
        '''
        Get all possible charter companies and result as list of forall.fleet_operator.FleetOperator
        Used 1 time in year (or some month) by syncer.py
        '''
        # get information from service and parce it
        r = requests.post("http://ws.nausys.com/CBMS-external/rest/catalogue/v6/charterCompanies", data='{{"username":"{0}", "password":"{1}"}}'.format(USER_NAME_NAUSYS, PASSWORD_NAUSYS), headers={'content-type': 'application/json'})
        result_as_obj = cjson.decode(r.text)
        
        result = []
        for operator in result_as_obj["companies"]:
            cur_operator = forall.fleet_operator.FleetOperator(OPERATOR_ID_NAUSYS, operator["id"])
            for key, value in operator.iteritems():
                cur_operator.parameters[key] = str(value)[0:127]
            result.append(cur_operator)
        return result

    def GetEquipmentAndCategory(self):
        '''
        Ask dictionary with possible additional equipment and equipment category from operator 
        Used 1 time in year (or some month) by syncer.py
        '''
        # result of this fuction is 2 lists
        result = {"equipment": [], "category":[]}
        # get information from service and parce it
        r = requests.post("http://ws.nausys.com/CBMS-external/rest/catalogue/v6/equipment", data='{{"username":"{0}", "password":"{1}"}}'.format(USER_NAME_NAUSYS, PASSWORD_NAUSYS), headers={'content-type': 'application/json'})
        result_as_obj = cjson.decode(r.text)
        
        # parse all equipment
        for equipment in result_as_obj["equipment"]:
            result["equipment"].append({"id": equipment["id"], "name": equipment["name"]["textEN"].strip(), "categoryId": equipment.get("categoryId", None)})

        # get information from service and parce it
        r = requests.post("http://ws.nausys.com/CBMS-external/rest/catalogue/v6/equipmentCategories", data='{{"username":"{0}", "password":"{1}"}}'.format(USER_NAME_NAUSYS, PASSWORD_NAUSYS), headers={'content-type': 'application/json'})
        result_as_obj = cjson.decode(r.text)
        
        #  and parse all categories
        for category in result_as_obj["equipmentCategories"]:
            result["category"].append({"id": category["id"], "name": category["name"]["textEN"].strip()})
        return result
    
    def GetYachtCategories(self):
        '''
        Ask dictionary with possible Yacht Categories
        This is secondary function, not interface, used only by GetBoatModels
        '''
        
        result = {}
        
        # get information from service and parce it
        r = requests.post("http://ws.nausys.com/CBMS-external/rest/catalogue/v6/yachtCategories", data='{{"username":"{0}", "password":"{1}"}}'.format(USER_NAME_NAUSYS, PASSWORD_NAUSYS), headers={'content-type': 'application/json'})
        result_as_obj = cjson.decode(r.text)
        
        for category in result_as_obj["categories"]:
            result[category["id"]] = category["name"]["textEN"].strip()
        return result
        
    
    def GetBoats(self, charters_company_ids):
        '''
        Used 1 time in year (or some month) by syncer.py
        '''
        result = []
        for charters_company_id in charters_company_ids:
            # get information from service and parce it
            r = requests.post("http://ws.nausys.com/CBMS-external/rest/catalogue/v6/yachts/{}".format(charters_company_id), data='{{"username":"{0}", "password":"{1}"}}'.format(USER_NAME_NAUSYS, PASSWORD_NAUSYS), headers={'content-type': 'application/json'})
            result_as_obj = cjson.decode(r.text)
            
            for boat in result_as_obj["yachts"]:
                cur_boat = forall.boat.Boat(OPERATOR_ID_NAUSYS, boat["id"], boat["yachtModelId"])
                for key, value in boat.iteritems():
                    if key == "mainPictureUrl":
                        cur_boat.images.append({"url": value, "type": 0})
                    elif key == "picturesURL":
                        for url in value:
                            cur_boat.images.append({"url": url, "type": 1})
                    elif key == "standardYachtEquipment":
                        for equipment in value:
                            cur_boat.equipment.append({"id": equipment["equipmentId"],
                                                       "value": equipment["quantity"],
                                                       "unit": "",
                                                       "name_group": None,
                                                       "comment": equipment["comment"].get("textEN", "")}) 
                    elif key == "locationId":
                        cur_boat.ports.append({"id_place": value, "level": LEVELS_NAUSYS["locations"]["level"], "id_type":1})
                    else:
                        cur_boat.parameters[key] = str(value)[0:127]
                result.append(cur_boat)
        return result

    def GetBoatModels(self):
        '''
        Get all available yachts models from operator
        
        Used 1 time in year (or some month) by syncer.py
        '''
        yachtCategories = self.GetYachtCategories()
        result = []
        
        # get information from service and parce it
        r = requests.post("http://ws.nausys.com/CBMS-external/rest/catalogue/v6/yachtModels", data='{{"username":"{0}", "password":"{1}"}}'.format(USER_NAME_NAUSYS, PASSWORD_NAUSYS), headers={'content-type': 'application/json'})
        result_as_obj = cjson.decode(r.text)
        
        for model in result_as_obj["models"]:
            cur_model = forall.boat_model.BoatModel(OPERATOR_ID_NAUSYS, model["id"])
            for key, value in model.iteritems():
                if key == "yachtCategoryId":
                        cur_model.parameters["yachtCategory"] = yachtCategories.get(value, "")
                cur_model.parameters[key] = unicode(value)[0:127]
            result.append(cur_model)
        return result
    
    def SearchBoat(self, filter_search):
        '''
        Run every time we need find boat. Not for syncing, only for service 
        '''
        # !!!!Period should be aligned to saturday - global yacht booking standart
        request_filter = {
              "credentials": {
                    "username":USER_NAME_NAUSYS,
                    "password":PASSWORD_NAUSYS
                    },
              "periodFrom":filter_search.GetDepartDate().strftime("%d.%m.%Y"),
              "periodTo":filter_search.GetFinishDate().strftime("%d.%m.%Y"),
              "resultsPerPage":filter_search.results_per_page,
              "resultsPage":filter_search.current_page
            }
        request_filter[LEVELS_NAUSYS2[filter_search.IDsForPlaces[OPERATOR_ID_NAUSYS]["level"]]] = [filter_search.IDsForPlaces[OPERATOR_ID_NAUSYS]["id"]]
        
        # Exceptions was used, because search result can be empty with hi possibility
        try:
            # get information from service
            r = requests.post("http://ws.nausys.com/CBMS-external/rest/yachtReservation/v6/freeYachtsSearch", data=cjson.encode(request_filter), headers={'content-type': 'application/json'})
        except:
            return forall.search_result.SearchResult(id_operator=self.operator_id,
                                                   total_count=0,
                                                   total_pages=0)
        # Such cases have happened
        if r.status_code <> 200:
            return forall.search_result.SearchResult(id_operator=self.operator_id,
                                                   total_count=0,
                                                   total_pages=0)
        # and parce it
        result_as_obj = cjson.decode(r.text)
        result = forall.search_result.SearchResult(id_operator=self.operator_id,
                                                   total_count=result_as_obj.get("totalCount", 0),
                                                   total_pages=result_as_obj.get("totalPages", 0))
        if "freeYachtsInPeriod" in result_as_obj:
            for one_yacht in result_as_obj["freeYachtsInPeriod"]:
                result.AppendBoatFromSearch(boat_id=one_yacht["yachtId"],
                                            price_for_client=one_yacht["price"]["clientPrice"],
                                            price_by_pricelist=one_yacht["price"]["priceListPrice"],
                                            discounts_in_procent=one_yacht["price"]["discounts"][0]["amount"])
        return result

    def CheckBoatFree(self, filter_params_one_boat):
        '''
        Check if one founded boat is available for booking
        Lask check before booking 
        '''

        # !!!!Period should be aligned to saturday - global yacht booking standart
        request_filter = {
              "credentials": {
                    "username":USER_NAME_NAUSYS,
                    "password":PASSWORD_NAUSYS
                    },
              "periodFrom":filter_params_one_boat.GetDepartDate().strftime("%d.%m.%Y"),
              "periodTo":filter_params_one_boat.GetFinishDate().strftime("%d.%m.%Y"),
              "yachts":[filter_params_one_boat.id_boat]
            }
        
        # Exceptions was used, because search result can be empty with hi possibility
        try:
            # get information from service
            r = requests.post("http://ws.nausys.com/CBMS-external/rest/yachtReservation/v6/freeYachts", data=cjson.encode(request_filter), headers={'content-type': 'application/json'})
        except:
            return forall.search_result.SearchResult(id_operator=self.operator_id,
                                                   total_count=0,
                                                   total_pages=0)
        # Such cases have happened
        if r.status_code <> 200:
            return forall.search_result.SearchResult(id_operator=self.operator_id,
                                                   total_count=0,
                                                   total_pages=0)
        # and parce it
        result_as_obj = cjson.decode(r.text)
        result = forall.search_result.SearchResult(id_operator=self.operator_id,
                                                   total_count=len(result_as_obj.get("freeYachts", [])),
                                                   total_pages=len(result_as_obj.get("freeYachts", [])))
        if "freeYachts" in result_as_obj:
            for one_yacht in result_as_obj["freeYachts"]:
                result.AppendBoatFromSearch(boat_id=one_yacht["yachtId"],
                                            price_for_client=one_yacht["price"]["clientPrice"],
                                            price_by_pricelist=one_yacht["price"]["priceListPrice"],
                                            discounts_in_procent=one_yacht["price"]["discounts"][0]["amount"])
        return result    

    def SearchCriteria(self):
        '''
        Not used. For future.
        '''
        
        request_filter = {
                    "username":USER_NAME_NAUSYS,
                    "password":PASSWORD_NAUSYS
                    }

        # get information from service and parce it
        r = requests.post("http://ws.nausys.com/CBMS-external/rest/yachtReservation/v6/freeYachtsSearchCriteria", data=cjson.encode(request_filter), headers={'content-type': 'application/json'})
        print r.text
    
    def BookYacht(self, UserInfo, date_from, date_to, yacht_id):
        '''
        Not yet implemented
        '''
        pass
    
if __name__ == '__main__':
    '''
    This is testing func for debug
    '''
    oper = OperatorNausys()
    oper.SearchCriteria()
    exit(1)
    filter_params = forall.search_filter.SearchFilterParameters(source_place_name='Croatia', depart_date_from=datetime.date(2017, 7, 23), count_week=1)
    print filter_params.toJSON()
    res = oper.SearchBoat(filter_params)
    # charters_company_ids = [x.local_operator_id for x in oper.GetFleetOperators()]
    # res = oper.GetBoats(charters_company_ids)
    
