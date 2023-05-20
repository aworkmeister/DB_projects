__author__ = 'abigail'
"""
Moves people with status ='ineligible' and 'complete' in registry to 'active' after 30 days
"""
import redcap
import os
from redcap import Project
import datetime

if __name__ == '__main__':
    # Predefined variables
    serviceurl = 'https://redcap.vanderbilt.edu/api/'
    vmacregistry = Project(serviceurl, os.environ['VMAC_REGISTRY'])
    
    # Download data from registry
    data = vmacregistry.export_records(fields=['vmac_id', 'status', 'status_ineligible', 'referral_date'])
    
    # get list of vmac ids
    vmacids = list(set([item['vmac_id'] for item in data]))
    
    # Build a dictionary with most recent registry study referral event
    registry_recent = []
    for item in vmacids:
        info = [i for i in data if i['vmac_id'] == item][-1]  # gets most recent event
        registry_recent.append(info)
    
    # check the registry database to see if people have status=7(complete) at the last study referral. 
    complete=[i for i in registry_recent if i['status'] == '7']
    
    # check the Registry database to see if people have status=6(ineligible) at the last study referral. 
    ineligible=[i for i in registry_recent if i['status'] == '6']
    
    #exclude people who are ineligible due to death
    #Print people without status_ineligible  
    move= [i for i in ineligible if i['status_ineligible'] !=1]
    blank= [i for i in ineligible if i['status_ineligible'] == '']
    for item in blank:
        to_sync = item['vmac_id']
        print("vmac_id without status_ineligible : {to_sync}".format(to_sync=to_sync))
    
    #make dictionary with both complete and ineligible people
    total=complete+move
    
    #print people that do not have referral_date from last event
    no_date=[i for i in total if i['referral_date'] == '']
    for item in no_date:
        to_sync = item['vmac_id']
        print("vmac_id without referral_date : {to_sync}".format(to_sync=to_sync))
        
    #make dictionary with people that have referral_date filled out    
    total_date=[i for i in total if i['referral_date'] != '']
    
    #convert date from string to date time format
    total_time_converted= []
    for item in total_date:
        info={}
        info['vmac_id'] = item['vmac_id']
        info['referral_date'] = datetime.datetime.strptime(item['referral_date'], "%Y-%m-%d")
        total_time_converted.append(info)
        
    # Build a dictionary to move people in the registry back to active
    upload = []
    for item in total_time_converted:
        info = {}
        delta= datetime.datetime.today()- item['referral_date']
        if delta.days >= 30:
            to_active = item['vmac_id']
            print("Syncing record to active : {to_active}".format(to_active=to_active), "- Days =", delta.days)
            info['vmac_id'] = item['vmac_id']
            info['redcap_repeat_instance'] = 'new'
            info['redcap_repeat_instrument'] = 'study_referral'
            info['status'] = '1'
            info['referral_date'] = datetime.date.today().strftime('%Y-%m-%d')
            info['study_referral_complete'] = '2'
        upload.append(info)
    
    #upload to redcap
    vmacregistry.import_records(upload)
    
    #print number of records
    print ("Number of records updated = ", len(upload) )
