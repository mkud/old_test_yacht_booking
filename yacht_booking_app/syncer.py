# -*- coding: utf-8 -*-
'''
Created on 7 jul 2017

@author: maxx

This script used for periodically (not often, per year) syncing info from operator to our database.
In database data usual store as "our_local_id" - "operator_id+local_operator id" - "name" - "value"
Types of syncs group in different functions.
'''

import os
import sys
import requests

import apis.api_sedna
import apis.api_nausys
import db
import smart_get_config

# Get database connection
data_base = db.DB(smart_get_config.global_config.get("database", "db_host"),
                  int(smart_get_config.global_config.get("database", "db_port")),
                  smart_get_config.global_config.get("database", "db_user"),
                  smart_get_config.global_config.get("database", "db_pass"),
                  smart_get_config.global_config.get("database", "db_name"))


def SyncPlaces(operator_api):
    '''
    Download places (regions, countries, ports)
    and save to database
    '''
    # remoce old data from database
    data_base.ClearAllLevelsPlacesForOperator(operator_api.operator_id)

    # get data from operator and save to database
    places = operator_api.GetPlaces()
    for place in places:
        data_base.AppendPlace(operator_api.operator_id, place.level, place.local_operator_id, place.name, place.local_operator_parent_id, place.parent_level, place.code, place.lat, place.lon)
        
def SyncFleetOperators(operator_api):
    '''
    Download yachts operators 
    and save to database
    '''
    # remoce old data from database
    data_base.ClearFleetOperators(operator_api.operator_id)

    # get data from operator and save to database
    fleet_operators = operator_api.GetFleetOperators()
    for fleet_operator in fleet_operators:
        data_base.AppendFleetOperator(fleet_operator.id_operator, fleet_operator.local_operator_id)
        for key, value in fleet_operator.parameters.iteritems():
            data_base.AppendFleetOperatorSettings(fleet_operator.id_operator, fleet_operator.local_operator_id, key, value)
    return [x.local_operator_id for x in fleet_operators] 

def SyncBoatModels(operator_api):
    '''
    Download yachts models 
    and save to database
    '''
    # remoce old data from database
    data_base.ClearBoatModel(operator_api.operator_id)

    # get data from operator and save to database
    models = operator_api.GetBoatModels()
    for model in models:
        data_base.AppendBoatModel(operator_api.operator_id, model.local_operator_id)
        for key, value in model.parameters.iteritems():
            data_base.AppendBoatModelSettings(operator_api.operator_id, model.local_operator_id, key, value)

def SyncBoats(operator_api, list_of_fleet_operators):
    '''
    Download yachts by operator_id 
    and save to database
    '''
    # remoce old data from database
    data_base.ClearBoats(operator_api.operator_id)

    # get data from operator and save to database
    boats = operator_api.GetBoats(list_of_fleet_operators)
    for boat in boats:
        data_base.AppendBoat(operator_api.operator_id, boat.local_operator_id, boat.boat_model)
        for key, value in boat.parameters.iteritems():
            data_base.AppendBoatSettings(operator_api.operator_id, boat.local_operator_id, key, value)
        for image in boat.images:
            data_base.AppendBoatImage(operator_api.operator_id, boat.local_operator_id, image["url"], image["type"])
        for equipment in boat.equipment:
            data_base.AppendBoatEquipment(operator_api.operator_id, boat.local_operator_id, equipment["id"], equipment["value"], equipment["unit"], equipment["name_group"], equipment["comment"])
        for port in boat.ports:
            data_base.AppendBoatPort(operator_api.operator_id, boat.local_operator_id, port["id_place"], port["level"], port["id_type"])


def SyncEquipmentAndCategory(operator_api):
    '''
    Download aditional equipment 
    and save to database
    '''
    # remoce old data from database
    data_base.ClearEquipment(operator_api.operator_id)
    data_base.ClearEquipmentGroup(operator_api.operator_id)

    # get data from operator and save to database
    equipmentAndCategory = operator_api.GetEquipmentAndCategory()
    for equipment in equipmentAndCategory["equipment"]:
        data_base.AppendEquipment(operator_api.operator_id, equipment["id"], equipment["name"], equipment["categoryId"])
    for category in equipmentAndCategory["category"]:
        data_base.AppendEquipmentGroup(operator_api.operator_id, category["id"], category["name"])
    
def FetchAllBoatImages():
    '''
    Download all new yachts images  
    and save to files on disk
    and to database
    '''
    boat_images = data_base.GetAllBoatImagesForDownload()
    for boat_image in boat_images:
        response = requests.get(boat_image[1])
        if response.status_code == 200:
            local_url = "static/boat_images/{0}{1}".format(boat_image[0], os.path.splitext(boat_image[1])[1]) 
            with open(local_url, 'wb') as f:
                f.write(response.content)
            data_base.PutLocalBoatImage(boat_image[0], local_url)

def SyncExistedBoatImages():
    '''
    Sync all downloaded yachts images 
    and syncronize them by erase
    '''
    list_files_from_fs = set([u'static/boat_images/' + x for x in os.listdir('static/boat_images')])
    list_files_from_db = {x[1]: x[0] for x in data_base.GetAllBoatImagesForSync()}
    for file_name_in_fs in list_files_from_fs:
        if file_name_in_fs not in list_files_from_db:
            os.remove(file_name_in_fs)
    for file_name_in_db in list_files_from_db:
        if file_name_in_db not in list_files_from_fs:
            data_base.PutLocalBoatImage(list_files_from_db[file_name_in_db], None)
    

if __name__ == '__main__':
    # fully syncronization images with operators
    if 'images_fetch' in sys.argv:
        FetchAllBoatImages()
        exit(0)
    if 'images_remove' in sys.argv:
        SyncExistedBoatImages()
        exit(0)
    # fully syncronization images with operators
        
    # Init operator apies for using in sync functions 
    operator_sedna = apis.api_sedna.OperatorSedna()
    operator_nausys = apis.api_nausys.OperatorNausys()
    
    #SyncBoatModels(operator_nausys) # very long query
    #SyncBoatModels(operator_sedna)
    #SyncEquipmentAndCategory(operator_nausys)
    #SyncEquipmentAndCategory(operator_sedna)
    # SyncPlaces(operator_sedna)
    
    #list_operators = SyncFleetOperators(operator_sedna)
    #SyncBoats(operator_sedna, list_operators)
    #list_operators = SyncFleetOperators(operator_nausys)
    #SyncBoats(operator_nausys, list_operators)
    
    # FetchAllBoatImages()
    # SyncExistedBoatImages()
    # SyncPlaces(operator_nausys)
    # SyncFleetOperators(operator_nausys)
    
