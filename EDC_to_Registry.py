__author__ = 'abigail'
"""
Pull Data from Electronic Data Capture and Participant Tracking Database to fill Registry Database. Project must be specified.
Script fills in information for enrollment, withdrawal, and diagnosis data in Registry based on EDC and PTD.
"""
import redcap
import os
from redcap import Project

# REDCap variables
serviceurl = 'https://redcap.vanderbilt.edu/api/'

def get_cmd_line():
    """
        Take in command line input specifying the study
        :return: dict output with project name
        """
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--project", type=str, help="Study Project of interest", choices=['MAP', 'TAP'], required=True)
    args = parser.parse_args()
    cmd_dict = {'project': args.project}
    return cmd_dict

if __name__ == '__main__':
    # Get command line options and check them
    options = get_cmd_line()
    upload_enrollment = []
    upload_withdrawn = []
    upload_diagnosis = []
    # Connect to the appropriate redcap project
    if options['project'] == 'TAP':
        edc_database = Project(serviceurl, os.environ['TAP_ELECTRONIC_DATA_CAPTURE'])
        ptd_database = Project(serviceurl, os.environ['TAP_PARTICIPANT_TRACKING'])
        registry_database = Project(serviceurl, os.environ['VMAC_REGISTRY'])
    elif options['project'] == 'MAP':
        edc_database = Project(serviceurl, os.environ['VMAP_ELECTRONIC_DATA_CAPTURE'])
        ptd_database = Project(serviceurl, os.environ['VMAP_PARTICIPANT_TRACKING'])
        registry_database = Project(serviceurl, os.environ['VMAC_REGISTRY'])
    else:
        raise ValueError("Unrecognized or blank project name")

    # get data for each project
    # Download registry data
    registry_data = registry_database.export_records(
        fields=['vmac_id', 'tap_enrolled', 'tap_diagnosis', 'vmap_enrolled'])
    if options['project'] == 'TAP':
        # Download TAP EDC data at event enrollmentbaseline_arm_1
        edc_data_bl = edc_database.export_records(fields=['vmac_id', 'elig_outcome', 'd1_visit_date', 'ivp_d1_clinician_diagnosis_consensus_form_complete'],
                                                  events=['enrollmentbaseline_arm_1'])
        # Download TAP EDC data at all timepoints
        edc_data = edc_database.export_records(fields=['vmac_id', 'diagnosis', 'fvp_d1_clinician_diagnosis_consensus_form_complete','ivp_d1_clinician_diagnosis_consensus_form_complete'])
        # Download TAP PTD data
        ptd_data = ptd_database.export_records(fields=['vmac_id', 'withdraw', 'withdraw_date'])
    elif options['project'] == 'MAP':
        edc_data_bl = edc_database.export_records(fields=['vmac_id', 'vf_arrival_date_time'],
                                                  events=['enrollmentbaseline_arm_1'])
        # Download TAP EDC data at all timepoints
        edc_data = edc_database.export_records(fields=['vmac_id', 'diagnosis'])
        # Download VMAP PTD data
        ptd_data = ptd_database.export_records(fields=['vmac_id', 'withdraw', 'withdraw_date'])
    
    #determine who needs enrollment records synced
    if options['project'] == 'TAP':
        enrolled_ids = [item for item in edc_data_bl if item['elig_outcome'] == '1' and item['ivp_d1_clinician_diagnosis_consensus_form_complete']== '2']
        registry_ids = [item['vmac_id'] for item in registry_data if item['tap_enrolled'] == '']
    elif options['project'] == 'MAP':
        enrolled_ids = [item for item in edc_data_bl if item['vf_arrival_date_time'] != '']
        #change date time to just date
        #this is definitely not the best way to do this but couldn't figure out how to convert date time to just date
        for vmac_id in enrolled_ids:
            vf_arrival_date= vmac_id["vf_arrival_date_time"][0:10]
            vmac_id["vf_arrival_date"] = vf_arrival_date
        registry_ids = [item['vmac_id'] for item in registry_data if item['vmap_enrolled'] == '']
    data_to_sync = [item for item in enrolled_ids if item['vmac_id'] in registry_ids]
    #print(data_to_sync)
    # Build dictionary to upload to registry for each enrollment
    for item in data_to_sync:
        info = {}
        info_static = {}
        to_sync = item['vmac_id']
        print("Syncing enrollment record {to_sync}".format(to_sync=to_sync))
        # static fields: mark new enrollments as yes in the VMAC Registry
        info_static['vmac_id'] = item['vmac_id']
        if options['project'] == 'TAP':
            info_static['tap_enrolled'] = 'yes'
        elif options['project'] == 'MAP':
            info_static['vmap_enrolled'] = 'yes'
        upload_enrollment.append(info_static)
        # repeating fields: create new instance of study referral, for TAP, referral_date = d1_date_visit, for MAP, referal_date=vf_arrival_date
        info['vmac_id'] = item['vmac_id']
        info['redcap_repeat_instance'] = 'new'
        info['redcap_repeat_instrument'] = 'study_referral'
        info['status'] = '5'
        info['study_referral_complete'] = '2'
        if options['project'] == 'TAP':
            info['study_name'] = '17'
            info['referral_date'] = item['d1_visit_date']
        elif options['project'] == 'MAP':
            info['study_name'] = '16'
            info['referral_date'] = item['vf_arrival_date']
        upload_enrollment.append(info)
    #print(upload_enrollment)
    # upload to redcap
    registry_database.import_records(upload_enrollment)
    
    # check the Participant Tracking database to see if people have withdrawn = 1 at the last event that they have in PTD. If so, mark the vmap_enrolled variable = withdrawn and create a new instance of study referral with status = 6 (ineligible), status_ineligible = 2 (Ineligible reason = withdrawal), study_name = 16 (VMAP2.0) and withdraw_date= withdraw_date
    if options['project'] == 'TAP':
        # pull withdrawn instances from registry
        registrywithdrawn = [item for item in registry_data if item['tap_enrolled'] == 'withdrawn']
        # pull only withdraw instances from ptd
        ptdwithdrawn = [item for item in ptd_data if item['withdraw'] == '1' and item['withdraw_date'] != '']
    elif options['project'] == 'MAP':
        # pull withdrawn instances from registry
        registrywithdrawn = [item for item in registry_data if item['vmap_enrolled'] == 'withdrawn']
        # pull only withdraw instances from ptd
        ptdwithdrawn = [item for item in ptd_data if item['withdraw'] == '1' and item['withdraw_date'] != '']
    # get most recent withdrawn ptd event
    vmacids = list(set([item['vmac_id'] for item in ptdwithdrawn]))
    registryvmacids = list([item['vmac_id'] for item in registrywithdrawn])
    # Build a dictionary with most recent withdrawn ptd event
    ptdwithdrawn_recent = []
    for item in vmacids:
        info = [i for i in ptdwithdrawn if i['vmac_id'] == item][-1]  # gets most recent event
        ptdwithdrawn_recent.append(info)
    # determine which records need updated
    withdraw_to_update = [i for i in ptdwithdrawn_recent if i['vmac_id'] not in registryvmacids]
    #create dictionaries with info that needs updated
    for item in withdraw_to_update:
        info = {}
        info_static = {}
        to_sync = item['vmac_id']
        print("Syncing withdrawal record {to_sync}".format(to_sync=to_sync))
        #static fields: mark new withdraws as withdrawn in the VMAC Registry
        info_static['vmac_id'] = item['vmac_id']
        if options['project'] == 'TAP':
            info_static['tap_enrolled'] = 'withdrawn'
        elif options['project'] == 'MAP':
            info_static['vmap_enrolled'] = 'withdrawn'
        upload_withdrawn.append(info_static)
        #repeating fields: create new instance of study referral, status = 6 (ineligible), status_ineligible = 2 (Ineligible reason = withdrawal), referral_date = withdraw_date
        info['vmac_id'] = item['vmac_id']
        info['redcap_repeat_instance'] = 'new'
        info['redcap_repeat_instrument'] = 'study_referral'
        info['status'] = '6'
        info['status_ineligible']= '2'
        info['referral_date'] = item['withdraw_date']
        info['study_referral_complete']= '2'
        if options['project'] == 'TAP':
            info['study_name'] = '17'
        elif options['project'] == 'MAP':
            info['study_name'] = '16'
        upload_withdrawn.append(info)
    #print(upload_withdrawn)
    #upload to redcap
    registry_database.import_records(upload_withdrawn)
    
    #Determine which diagnoses need updated
    if options['project'] == 'TAP':
        #remove edc_data instances with empty diagnosis and consensus variable not complete
        edc_diag= [item for item in edc_data if item['diagnosis'] != '']
        edc_diagnosis=[]
        for item in edc_diag:
            info={}
            if item['redcap_event_name'] == 'enrollmentbaseline_arm_1' and item['ivp_d1_clinician_diagnosis_consensus_form_complete'] == '2':
                info['vmac_id'] = item['vmac_id']
                info['diagnosis']= item['diagnosis']
                info['fvp_d1_clinician_diagnosis_consensus_form_complete'] = item['fvp_d1_clinician_diagnosis_consensus_form_complete']
                info['ivp_d1_clinician_diagnosis_consensus_form_complete'] = item['ivp_d1_clinician_diagnosis_consensus_form_complete']
                info['redcap_event_name'] = item['redcap_event_name']
                edc_diagnosis.append(info)
            elif item['redcap_event_name'][-14:] == 'followup_arm_1' and item['fvp_d1_clinician_diagnosis_consensus_form_complete'] == '2':
                info['vmac_id'] = item['vmac_id']
                info['diagnosis']= item['diagnosis']
                info['fvp_d1_clinician_diagnosis_consensus_form_complete'] = item['fvp_d1_clinician_diagnosis_consensus_form_complete']
                info['ivp_d1_clinician_diagnosis_consensus_form_complete'] = item['ivp_d1_clinician_diagnosis_consensus_form_complete']
                info['redcap_event_name'] = item['redcap_event_name']
                edc_diagnosis.append(info)
            
        #get most recent event
        vmacids= list(set([item['vmac_id'] for item in edc_diagnosis]))

        # Build a dictionary with most recent diagnosis
        recents = []
        for item in vmacids :
            edc_recent_dx = [i for i in edc_diagnosis if i['vmac_id'] == item][-1]
            recents.append(edc_recent_dx)

        for item in recents :
            tap_diagnosis_reg = [i for i in registry_data if i['vmac_id'] == item['vmac_id']][0]
            if tap_diagnosis_reg['tap_diagnosis'] != item['diagnosis'] :
                info = {}
                to_sync = item['vmac_id']
                print("Syncing diagnosis record {to_sync}".format(to_sync=to_sync))
                info['vmac_id'] = item['vmac_id']
                info['tap_diagnosis'] = item['diagnosis']
                upload_diagnosis.append(info)
    #print(upload_diagnosis)
    #upload to redcap
    registry_database.import_records(upload_diagnosis)
