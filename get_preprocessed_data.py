# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 19:48:15 2018

@author: Daniel Solá
"""

import importlib
from resources.queries import *
from resources.mappings import *
from services import preprocessing_service
from services.query_service import query_database
import pandas as pd
from functools import reduce
importlib.reload(resources)

class DemographicData():
    
    def __get_ages(self):
        
        ages = query_database(AGE_QUERY)
        
        ages['age'] = ages.apply(lambda x: x['age'] if x['age'] < 300 else 91.4, axis = 1)
        
        return ages
        
    def __get_genders(self):
        
        return query_database(GENDER_QUERY)
    	
    
    def __get_marital_status(self):
        
        marital_status_df = query_database(MARITAL_STATUS_QUERY)
        
        return preprocessing_service.group_marital_status(marital_status_df)
    
    def __get_religion(self):
        
        religion_df = query_database(RELIGION_QUERY)
        
        return preprocessing_service.group_religion(religion_df)
    
    def __get_ethnic_group(self):
        
        ethnic_group_df = query_database(ETHNICITY_QUERY)
        
        return preprocessing_service.group_ethnic_groups(ethnic_group_df)
    
    def get_demographic_data(self):
        
        age             = self.__get_ages()
        gender          = self.__get_genders()
        marital_status  = self.__get_marital_status()
        religion        = self.__get_religion()
        ethnic_group    = self.__get_ethnic_group()
        
        demographic_dfs = [age, gender, marital_status, religion, ethnic_group]
        
        return reduce(lambda left, right: pd.merge(left,right, on = 'hadm_id'), demographic_dfs)
    
class Measures():
    
    def get_lab_data(self):
        
        lab_results_dfs = []
    
        for measure in LAB_TEST:
            
           lab_test_df = query_database(f'''SELECT 
                                      hadm_id,
                                      avg(valuenum) AS AVG_{measure['test']},
                                      stddev(valuenum) AS STD_{measure['test']}
                                      FROM labevents
                                      WHERE itemid = {measure['itemid']} 
                                      GROUP BY hadm_id
                                      LIMIT 100 ''')
           
           lab_results_dfs.append(lab_test_df)
          
        return reduce(lambda left, right: pd.merge(left,right, on = 'hadm_id'), lab_results_dfs).fillna(0)

    def get_physio_data(self):
        
        physio_measures_dfs = []
        
        for measure in PHYSIO_MEASURES:
            
            print(f'''Querying {measure['name']}...''' )
            
            physio_measure = query_database(f'''SELECT 
                                            hadm_id,
                                            avg(valuenum) AS AVG_{measure['name']},
                                            stddev(valuenum) AS STD_{measure['name']},
                                            count(valuenum) AS COUNT_{measure['name']}
                                            FROM chartevents
                                            WHERE itemid in ({measure['itemid']})
                                            GROUP BY hadm_id
                                            LIMIT 20''')
            physio_measures_dfs.append(physio_measure)
            
        return reduce(lambda left, right: pd.merge(left, right, how = 'outer', on = 'hadm_id'), a)
    

class AdministrativeData():

    def get_services():
    
        services = query_database(queries.SERVICE_QUERY)
            
        relevant_services_list = list(services.apply(lambda x: preprocessing_service.get_relevant_admission_service(x['hadm_id'], services), axis = 1))
    
        relevant_services_df = pd.DataFrame(relevant_services_list, columns = ['hadm_id','service'])
    
        return relevant_services_df.groupby("hadm_id").first()
    

