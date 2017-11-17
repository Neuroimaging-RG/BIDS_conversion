import os


def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """

    t1w = create_key('anat/sub-{subject}_T1w')
    t2w = create_key('anat/sub-{subject}_T2w')
    flair = create_key('anat/sub-{subject}_flair')
    dwi = create_key('dwi/sub-{subject}_acq-{dwi_type}_dwi')    
    dwi_sbref = create_key('dwi/sub-{subject}_sbref')
    asl = create_key('asl/sub-{subject}_task-rest_asl')
    rest = create_key('func/sub-{subject}_task-rest_bold')
    rest_sbref = create_key('func/sub-{subject}_task-rest_sbref')
    fmap = create_key('fmap/sub-{subject}_{fmap_type}')
    swi = create_key('swi/sub-{subject}_{swi_type}')
    info = {t1w: [], t2w: [], flair: [], dwi: [], dwi_sbref: [], asl:[], rest:[], rest_sbref:[], fmap:[], swi:[]}

    # CM notes - 
    # the BID convention for perfusion has not be finalised yet see "useful links" on git hub for asl working doc
	# they have not decided if asl should go in func or own folder I have made a asl folder, rather than put it in func 
    # also the BIDS convention for SWI has not been finalised yet (again see useful links for swi working group
    # in main BIDS specification says SWI is anat but in working doc suggests swi folder as you can get many files for swi and QSM
    # so I have created separate folder too for swi
    #
    # last_run = len(seqinfo) don't think need this
    #################
    
    for idx, s in enumerate(seqinfo):
        """
        The namedtuple `s` contains the following fields:

        * total_files_till_now
        * example_dcm_file
        * series_id
        * dcm_dir_name
        * unspecified2
        * unspecified3
        * dim1
        * dim2
        * dim3
        * dim4
        * TR
        * TE
        * protocol_name
        * is_motion_corrected
        * is_derived
        * patient_id
        * study_description
        * referring_physician_name
        * series_description
        * image_type
        """
        # anatomy scans
        if (s.dim3 == 208) and (s.dim4 == 1) and ('T1' in s.protocol_name):
            info[t1w] = [s.series_id]
        if ('T2_BLADE' in s.protocol_name):
            info[t2w] = [s.series_id]
        if ('T2_FLAIR' in s.protocol_name):
            info[flair] = [s.series_id]

        # diffusion scans
        if (s.dim4 == 105) and ('Diff' in s.protocol_name):
            info[dwi].append({'item': s.series_id,'dwi_type': 'data'})
        if ('BU_AP' in s.series_description):
            info[dwi].append({'item': s.series_id,'dwi_type': 'BU'})
        if ('BD_PA_1' in s.series_description):
            info[dwi].append({'item': s.series_id,'dwi_type': 'BD1'})
        if ('BD_PA_2' in s.series_description):
            info[dwi].append({'item': s.series_id,'dwi_type': 'BD2'})
        if ('BD_PA_3' in s.series_description):
            info[dwi].append({'item': s.series_id,'dwi_type': 'BD3'})
        if ('Diff_MB3_SBRef' in s.series_description):
            info[dwi_sbref] = [s.series_id]
        
        # perfusion scan
        if (s.dim4 == 17) and ('pcasl' in s.protocol_name):
            info[asl] = [s.series_id]

        # functional scan
        if (s.dim4 == 490) and ('bold' in s.protocol_name):
            info[rest] = [s.series_id]
        if (s.dim4 == 1) and ('bold' in s.protocol_name):
            info[rest_sbref] = [s.series_id]

        # field map        
        if (s.dim3 == 128) and ('field_map' in s.protocol_name):
            info[fmap].append({'item': s.series_id,'fmap_type': 'magnitude'})
        if (s.dim3 == 64) and ('field_map' in s.protocol_name):
            info[fmap].append({'item': s.series_id,'fmap_type': 'phasediff'})
        
        # susceptibility weighted
        if  ('SWI' in s.protocol_name) and ('Mag' in s.series_description):
            info[swi].append({'item': s.series_id,'swi_type': 'part-mag_GRE'})
        if  ('SWI' in s.protocol_name) and ('Pha' in s.series_description):
            info[swi].append({'item': s.series_id,'swi_type': 'part-phase_GRE'})
        if  ('SWI' in s.protocol_name) and ('mIP' in s.series_description):
            info[swi].append({'item': s.series_id,'swi_type': 'minIP'})
        if  ('SWI' in s.protocol_name) and ('SWI' in s.series_description):
            info[swi].append({'item': s.series_id,'swi_type': 'swi'})

    return info
