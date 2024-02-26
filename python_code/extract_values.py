from nilearn.input_data import NiftiMasker
import os, glob
from os.path import join as opj
import pandas as pd
import numpy as np

ALL_SUB = True

derivative_dir = '/projects/kuhl_lab/wanjiag/MONSTERA/derivatives/'
rois = ['evc_2_epi_thre_0.5_masked', 'ppa_mni_2_epi_thre_0.5_masked']
hippo_subfields = ['ashs/body/ca1-body_thre_0.5_masked', 'ashs/body/ca23dg-body_thre_0.5_masked']

#rois = ['angular_gyrus_2_epi_thre_0.5_masked', 'evc_2_epi_thre_0.5_masked', 'hippocampus_2_epi_thre_0.5_masked', 'ppa_mni_2_epi_thre_0.5_masked']
#hippo_subfields = ['ashs/body/ca1-body_thre_0.5_masked', 'ashs/body/ca23dg-body_thre_0.5_masked',
#                   'ashs/whole/ca1_thre_0.5_masked', 'ashs/whole/ca23dg_thre_0.5_masked']


if ALL_SUB:
    preprocess_dir = '/projects/kuhl_lab/wanjiag/MONSTERA/derivatives/preprocess'
    f_list = [x for x in glob.glob(os.path.join(preprocess_dir, '*sub-MONSTERA*/'))]
    subs = list(map(lambda f: f[len(os.path.commonpath(f_list))+1:-1], f_list))
    subs.sort()
    print(subs)

    bad = ['sub-MONSTERA01', 'sub-MONSTERA02', 'sub-MONSTERA03', 'sub-MONSTERA04', 'sub-MONSTERA05',
            'sub-MONSTERA13', 'sub-MONSTERA14', 'sub-MONSTERA20', 'sub-MONSTERA23', 'sub-MONSTERA24', 'sub-MONSTERA27', 
            'sub-MONSTERA30', 'sub-MONSTERA34']

    sublist = list(set(subs) - set(bad))
    sublist.sort()
    
    print(sublist)
else:
    sublist = ['sub-MONSTERA53']

    
print(sublist)
session_list = []
for i in range(1,11):
    session_list.append('task-{:02d}'.format(i))
    
for subnum in sublist:
    
    output_dir = opj(derivative_dir,'csv_files', 'fMRI', subnum)
    
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    for roi in rois:
        region_mask = opj(derivative_dir,'rois/{}/{}.nii.gz'.format(subnum, roi))
        print(roi, region_mask)
        masker = NiftiMasker(region_mask)

        for session in session_list:

            if (subnum == 'sub-MONSTERA29' and session == 'task-02'):
                continue 

            file_dir = opj(derivative_dir, 'preprocess', subnum, '{}_{}_desc-preproc_bold_trim6_denoise_z-scored.nii.gz'
                           .format(subnum, session))
            print(session, file_dir)
            region_data = masker.fit_transform(file_dir)
            
            output_file = opj(output_dir, '{}_{}_{}.csv'.format(roi, subnum, session))
            region_data = pd.DataFrame(region_data)
            region_data["run"] = session
            region_data["sub"] = subnum
            region_data["roi"] = roi
            region_data.to_csv(output_file, index=True)
            
    for roi in hippo_subfields:
        region_mask = opj(derivative_dir,'rois/{}/{}.nii.gz'.format(subnum, roi))
        print(roi, region_mask)
        masker = NiftiMasker(region_mask)

        for session in session_list:

            if (subnum == 'sub-MONSTERA29' and session == 'task-02'):
                continue

            file_dir = opj(derivative_dir, 'preprocess', subnum, '{}_{}_desc-preproc_bold_trim6_denoise_z-scored.nii.gz'
                           .format(subnum, session))
            print(session, file_dir)
            region_data = masker.fit_transform(file_dir)
            
            name = roi.split('/')[-1]
            output_file = opj(output_dir, '{}_{}_{}.csv'.format(name, subnum, session))
            region_data = pd.DataFrame(region_data)
            region_data["run"] = session
            region_data["sub"] = subnum
            region_data["roi"] = roi
            region_data.to_csv(output_file, index=True)
