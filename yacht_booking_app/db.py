# -*- coding: utf-8 -*-
import threading
import sys
import logging
import MySQLdb
import smart_get_config

if smart_get_config.global_config.get("main", "debug") == "0":
    logging.basicConfig(filename=smart_get_config.global_config.get("main", "log_file"), level=logging.DEBUG, format='%(asctime)s %(message)s')

def bug_report(file_stream=None):
    if sys.exc_info() != (None, None, None): 
        last_type, last_value, last_traceback = sys.exc_info()
    else: 
        last_type, last_value, last_traceback = sys.last_type, sys.last_value, sys.last_traceback  # @UndefinedVariable
    tb, descript = last_traceback, []
    while tb:
        fname, lno = tb.tb_frame.f_code.co_filename, tb.tb_lineno
        descript.append('\tFile "%s", line %s, in %s\n' % (fname, lno, tb.tb_frame.f_code.co_name))
        tb = tb.tb_next
    descript.append('%s : %s\n' % (last_type.__name__, last_value))
    if file_stream:
        for i in descript:
            file_stream.write(i)
        file_stream.flush()
    else:
        for i in descript:
            sys.stderr.write(i)
            logging.warning(i)


class DB(object):
    def __init__(self, host, port=3306, user='heat',
                 password='123456', db='heat_db'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db
        self.db = None
        self.cursor = None
        self.reconnect_db()
        self.lock = threading.Lock()

    def reconnect_db(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.db is not None:
            self.db.close()
        self.db = MySQLdb.connect(host=self.host,
                                  port=self.port,
                                  user=self.user,
                                  passwd=self.password,
                                  db=self.db_name,
                                  charset='utf8')
        self.db.autocommit(True)
        self.cursor = self.db.cursor()

    def close(self):
        self.db.close()

    def do_query_Maxx(self, sql, parameters, need_to_fetch_more_results=False):
        """
        Execute SQL query
        """
        try:
            if self.lock.locked():
                logging.info("MAXX!:is LOCKED")
            with self.lock:
                while True:
                    try:
                        self.cursor.execute(sql, parameters)
                        if need_to_fetch_more_results:
                            ret = self.cursor.fetchall()
                            while self.cursor.nextset():
                                pass
                            return ret
                        else:
                            return self.cursor.fetchall()
                    except MySQLdb.Error, e:  # @UndefinedVariable
                        logging.warning("execute_sql: Error MySQL " + e.args[1])
                        logging.warning("Query " + sql)
                        logging.warning("Parameters " + str(parameters))
                        logging.warning("Code - " + str(e.args[0]))
                        if 2000 <= e.args[0] <= 2020:
                            self.reconnect_db()
                            continue
                        raise
        except:
            bug_report()

    def ClearAllLevelsPlacesForOperator(self, id_operator):
        query = u"""CALL clear_alllevels_places_for_operator(%s)"""
        try:
            return self.do_query_Maxx(query, (id_operator,), True)
        except (IndexError, ValueError):
            return None

    def ClearLevelPlacesForOperator(self, id_operator, level):
        query = u"""CALL clear_level_places_for_operator(%s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, level), True)
        except (IndexError, ValueError):
            return None

    def AppendPlace(self, id_operator, level, local_operator_id, name, local_operator_parent_id, parent_level, code, lat, lon):
        query = u"""CALL append_place(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, level, local_operator_id, name, local_operator_parent_id, parent_level, code, lat, lon), True)
        except (IndexError, ValueError):
            return None

    def ClearFleetOperators(self, id_operator):
        query = u"""CALL clear_fleet_operators(%s)"""
        try:
            return self.do_query_Maxx(query, (id_operator,), True)
        except (IndexError, ValueError):
            return None

    def AppendFleetOperator(self, id_operator, local_operator_id):
        query = u"""CALL append_fleet_operator(%s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, local_operator_id), True)
        except (IndexError, ValueError):
            return None

    def AppendFleetOperatorSettings(self, id_operator, local_operator_id, name, value):
        query = u"""CALL append_fleet_operator_settings(%s, %s, %s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, local_operator_id, name, value), True)
        except (IndexError, ValueError):
            return None

    def ClearEquipment(self, id_operator):
        query = u"""CALL clear_equipment(%s)"""
        try:
            return self.do_query_Maxx(query, (id_operator,), True)
        except (IndexError, ValueError):
            return None

    def AppendEquipment(self, id_operator, local_operator_id, name, category_id):
        query = u"""CALL append_equipment(%s, %s, %s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, local_operator_id, name, category_id), True)
        except (IndexError, ValueError):
            return None

    def ClearEquipmentGroup(self, id_operator):
        query = u"""CALL clear_equipment_group(%s)"""
        try:
            return self.do_query_Maxx(query, (id_operator,), True)
        except (IndexError, ValueError):
            return None

    def AppendEquipmentGroup(self, id_operator, local_operator_id, name):
        query = u"""CALL append_equipment_group(%s, %s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, local_operator_id, name), True)
        except (IndexError, ValueError):
            return None

    def ClearBoatModel(self, id_operator):
        query = u"""CALL clear_boat_model(%s)"""
        try:
            return self.do_query_Maxx(query, (id_operator,), True)
        except (IndexError, ValueError):
            return None

    def AppendBoatModel(self, id_operator, local_operator_id):
        query = u"""CALL append_boat_model(%s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, local_operator_id), True)
        except (IndexError, ValueError):
            return None

    def AppendBoatModelSettings(self, id_operator, local_operator_id, name, value):
        query = u"""CALL append_boat_model_settings(%s, %s, %s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, local_operator_id, name, value), True)
        except (IndexError, ValueError):
            return None

    def ClearBoats(self, id_operator):
        query = u"""CALL clear_boats(%s)"""
        try:
            return self.do_query_Maxx(query, (id_operator,), True)
        except (IndexError, ValueError):
            return None

    def AppendBoat(self, id_operator, local_operator_id, local_operator_model_id):
        query = u"""CALL append_boat(%s, %s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, local_operator_id, local_operator_model_id), True)
        except (IndexError, ValueError):
            return None

    def AppendBoatSettings(self, id_operator, local_operator_id, name, value):
        query = u"""CALL append_boat_settings(%s, %s, %s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, local_operator_id, name, value), True)
        except (IndexError, ValueError):
            return None

    def AppendBoatImage(self, id_operator, local_operator_id, image, type_img):
        query = u"""CALL append_boat_image(%s, %s, %s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, local_operator_id, image, type_img), True)
        except (IndexError, ValueError):
            return None

    def GetAllBoatImagesForDownload(self):
        query = u"""CALL get_all_boat_images_for_download()"""
        try:
            return self.do_query_Maxx(query, (), True)
        except (IndexError, ValueError):
            return None

    def GetAllBoatImagesForSync(self):
        query = u"""CALL get_all_boat_images_for_sync()"""
        try:
            return self.do_query_Maxx(query, (), True)
        except (IndexError, ValueError):
            return None

    def PutLocalBoatImage(self, id_img, local_url):
        query = u"""CALL put_local_boat_image(%s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_img, local_url), True)
        except (IndexError, ValueError):
            return None

    def AppendBoatEquipment(self, id_operator, local_operator_id, id_equipment, value, unit, name_group, comment):
        query = u"""CALL append_boat_equipment(%s, %s, %s, %s, %s, %s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, local_operator_id, id_equipment, value, unit, name_group, comment), True)
        except (IndexError, ValueError):
            return None

    def AppendBoatPort(self, id_operator, local_operator_id, id_place, level_place, id_type):
        query = u"""CALL append_boat_port(%s, %s, %s, %s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, local_operator_id, id_place, level_place, id_type), True)
        except (IndexError, ValueError):
            return None

    def Site_GetPlaces(self, text):
        query = u"""CALL site_get_places(%s)"""
        try:
            return self.do_query_Maxx(query, (text,), True)
        except (IndexError, ValueError):
            return None

    def Map_Places(self, id_operator, list_places_as_string_join):
        query = u"""CALL site_map_places(%s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, list_places_as_string_join), True)
        except (IndexError, ValueError):
            return None
        
    def Site_GetManyBoats(self, id_operator, join_of_ids):
        query = u"""CALL site_get_many_boats(%s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_operator, join_of_ids), True)
        except (IndexError, ValueError):
            return None

    def Site_GetOnePlace(self, place_name):
        query = u"""CALL site_get_one_place(%s)"""
        try:
            return self.do_query_Maxx(query, (place_name,), True)
        except (IndexError, ValueError):
            return None

    def Site_GetClientInfo(self, id_client):
        query = u"""CALL site_get_client_info(%s)"""
        try:
            return self.do_query_Maxx(query, (id_client,), True)
        except (IndexError, ValueError):
            return None

    def Site_LoginClient(self, email, passwd):
        query = u"""CALL site_login_client(%s, %s)"""
        try:
            return self.do_query_Maxx(query, (email, passwd), True)
        except (IndexError, ValueError):
            return None
    
    def Site_RegisterClient(self, email, passwd, first_name, second_name):
        query = u"""CALL site_register_client(%s, %s, %s, %s)"""
        try:
            return self.do_query_Maxx(query, (email, passwd, first_name, second_name), True)
        except (IndexError, ValueError):
            return None

    def Site_CreateBooking(self, id_user, id_operator, id_yacht_operator_local, date_from, date_to, id_book_from_operator):
        query = u"""CALL site_create_booking(%s, %s, %s, %s, %s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_user, id_operator, id_yacht_operator_local, date_from, date_to, id_book_from_operator), True)
        except (IndexError, ValueError):
            return None

    def Site_CancelBooking(self, id_user, id_booking):
        query = u"""CALL site_cancel_booking(%s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_user, id_booking), True)
        except (IndexError, ValueError):
            return None

    def Site_GetAllUnfinishedBooking(self, id_user):
        query = u"""CALL site_get_all_unfinished_booking(%s)"""
        try:
            return self.do_query_Maxx(query, (id_user,), True)
        except (IndexError, ValueError):
            return None

    def Site_GetOneUnfinishedBooking(self, id_user, id_booking):
        query = u"""CALL site_get_one_unfinished_booking(%s, %s)"""
        try:
            return self.do_query_Maxx(query, (id_user, id_booking), True)
        except (IndexError, ValueError):
            return None
                                