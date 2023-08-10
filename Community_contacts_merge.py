__author__ = 'abigail'
"""
Pull Data from old community contact data base and fill to new database
"""
import redcap
import os
from redcap import Project

# REDCap variables
serviceurl = 'https://redcap.vanderbilt.edu/api/'
#old_database = Project(serviceurl, os.environ['OUTREACH_COMMUNITY_CONTACTS_TRACKING'])
#new_database = Project(serviceurl, os.environ['DEV_OUTREACH_COMMUNITY_CONTACTS_TRACKING'])

if __name__ == '__main__':
    # get all records from old DB 
    old_data_initial = old_database.export_records()
    
    #make list of each record where partner=2 and print so they can be reviewed because partner variables changed in new db
    partner2= [i for i in old_data_initial if i['partner'] == '2']
    lis_partner_2= []
    for item in partner2:
        id_partner=item['record_id']
        lis_partner_2.append(id_partner)
    print('Record ids where partner = 2 : ',lis_partner_2)
    
    #make list without partner=2 (partner variables changed in new db
    old_data = [i for i in old_data_initial if i['partner'] != '2']
    
    #Make a list of records for each number of contacts
    onecontact=[i for i in old_data if i['contact']=='1']
    twocontact=[i for i in old_data if i['contact2']=='1']
    threecontact=[i for i in old_data if i['contact3']=='1']
    fourcontact=[i for i in old_data if i['contact4']=='1']
    fivecontact=[i for i in old_data if i['contact5']=='1']
    sixcontact=[i for i in old_data if i['contact6']=='1']
    sevencontact=[i for i in old_data if i['contact7']=='1']
    eightcontact=[i for i in old_data if i['contact8']=='1']
    
    # Build list of all static records to upload to new database 
    upload_new=[]
    for item in old_data:
        info_static = {}
        to_sync = item['record_id']
        print("Syncing static record {to_sync}".format(to_sync=to_sync))
        # static fields: 
        info_static['record_id'] = item['record_id']
        info_static['partner'] = item['partner']
        info_static['organization_affiliation'] = item['organization_affiliation'] 
        info_static['job_title_position'] = item['job_title_position']
        info_static['partner_other'] = item['partner_other']
        info_static['first'] = item['first']
        info_static['last'] = item['last']
        info_static['salutation'] = item['salutation']
        info_static['salutation_other'] = item['salutation_other']
        info_static['street'] = item['street']
        info_static['city'] = item['city']
        info_static['zip'] = item['zip']
        info_static['email'] = item['email']
        info_static['newsletter'] = item['newsletter']
        info_static['phone_primary'] = item['phone']
        info_static['outreach_community_relations_tracking_complete'] = 1
        upload_new.append(info_static)
    
    # repeating fields: create new instance of study referral based on contact number 
    for item in onecontact:
        info={}
        to_sync = item['record_id']
        print("Syncing tp1 record {to_sync}".format(to_sync=to_sync))
        info['record_id'] = item['record_id']
        info['redcap_repeat_instance'] = '1'
        info['redcap_repeat_instrument'] = 'touch_point'
        info['tp_date'] = item['date']
        info['tp_purpose'] = 'building'
        info['tp_type'] = 'outbound'
        info['tp_result'] = 'comp'
        info['tp_user'] = item['team']
        info['tp_notes'] = item['notes']
        info['touch_point_complete'] = '2'
        upload_new.append(info)
    for item in twocontact:
        info={}
        to_sync = item['record_id']
        print("Syncing tp2 record {to_sync}".format(to_sync=to_sync))
        info['record_id'] = item['record_id']
        info['redcap_repeat_instance'] = '2'
        info['redcap_repeat_instrument'] = 'touch_point'
        info['tp_date'] = item['date2']
        info['tp_purpose'] = 'building'
        info['tp_type'] = 'outbound'
        info['tp_result'] = 'comp'
        info['tp_user'] = item['team2']
        info['tp_notes'] = item['notes2']
        info['touch_point_complete'] = '2'
        upload_new.append(info)
    for item in threecontact:
        info={}
        to_sync = item['record_id']
        print("Syncing tp3 record {to_sync}".format(to_sync=to_sync))
        info['record_id'] = item['record_id']
        info['redcap_repeat_instance'] = '3'
        info['redcap_repeat_instrument'] = 'touch_point'
        info['tp_date'] = item['date3']
        info['tp_purpose'] = 'building'
        info['tp_type'] = 'outbound'
        info['tp_result'] = 'comp'
        info['tp_user'] = item['team3']
        info['tp_notes'] = item['notes3']
        info['touch_point_complete'] = '2'
        upload_new.append(info)
    for item in fourcontact:
        info={}
        to_sync = item['record_id']
        print("Syncing tp4 record {to_sync}".format(to_sync=to_sync))
        info['record_id'] = item['record_id']
        info['redcap_repeat_instance'] = '4'
        info['redcap_repeat_instrument'] = 'touch_point'
        info['tp_date'] = item['date4']
        info['tp_purpose'] = 'building'
        info['tp_type'] = 'outbound'
        info['tp_result'] = 'comp'
        info['tp_user'] = item['team4']
        info['tp_notes'] = item['notes4']
        info['touch_point_complete'] = '2'
        upload_new.append(info) 
    for item in fivecontact:
        info={}
        to_sync = item['record_id']
        print("Syncing tp5 record {to_sync}".format(to_sync=to_sync))
        info['record_id'] = item['record_id']
        info['redcap_repeat_instance'] = '5'
        info['redcap_repeat_instrument'] = 'touch_point'
        info['tp_date'] = item['date5']
        info['tp_purpose'] = 'building'
        info['tp_type'] = 'outbound'
        info['tp_result'] = 'comp'
        info['tp_user'] = item['team5']
        info['tp_notes'] = item['notes5']
        info['touch_point_complete'] = '2'
        upload_new.append(info)
    for item in sixcontact:
        info={}
        to_sync = item['record_id']
        print("Syncing tp6 record {to_sync}".format(to_sync=to_sync))
        info['record_id'] = item['record_id']
        info['redcap_repeat_instance'] = '6'
        info['redcap_repeat_instrument'] = 'touch_point'
        info['tp_date'] = item['date6']
        info['tp_purpose'] = 'building'
        info['tp_type'] = 'outbound'
        info['tp_result'] = 'comp'
        info['tp_user'] = item['team6']
        info['tp_notes'] = item['notes6']
        info['touch_point_complete'] = '2'
        upload_new.append(info)
    for item in sevencontact:
        info={}
        to_sync = item['record_id']
        print("Syncing tp7 record {to_sync}".format(to_sync=to_sync))
        info['record_id'] = item['record_id']
        info['redcap_repeat_instance'] = '7'
        info['redcap_repeat_instrument'] = 'touch_point'
        info['tp_date'] = item['date7']
        info['tp_purpose'] = 'building'
        info['tp_type'] = 'outbound'
        info['tp_result'] = 'comp'
        info['tp_user'] = item['team7']
        info['tp_notes'] = item['notes7']
        info['touch_point_complete'] = '2'
        upload_new.append(info) 
    
    # upload to redcap
    #new_database.import_records(upload_new)
