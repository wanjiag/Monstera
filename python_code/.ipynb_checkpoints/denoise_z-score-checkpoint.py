import os
from os.path import join as opj
import glob
import numpy as np
import pandas as pd

import nibabel as nib
from nilearn.input_data import NiftiMasker
from nltools.data import Brain_Data, Design_Matrix
from nltools.stats import find_spikes 

derivative_dir = '/projects/kuhl_lab/wanjiag/MONSTERA/derivatives/'
preprocess_dir = '/projects/kuhl_lab/wanjiag/MONSTERA/derivatives/preprocess'
fmriprerp_dir = '/projects/kuhl_lab/wanjiag/MONSTERA/derivatives/fmriprep'
n_trunc = 6

tr = 1
outlier_cutoff = 3
filtcutoff=128 #high-pass filter

f_list = [x for x in glob.glob(os.path.join(preprocess_dir, '*sub-MONSTERA*/'))]
subs = list(map(lambda f: f[len(os.path.commonpath(f_list))+1:-1], f_list))
subs.sort()
print(subs)

bad = ['sub-MONSTERA01', 'sub-MONSTERA02', 'sub-MONSTERA03', 'sub-MONSTERA04', 'sub-MONSTERA05',
        'sub-MONSTERA13', 'sub-MONSTERA14', 'sub-MONSTERA20', 'sub-MONSTERA23', 'sub-MONSTERA24', 'sub-MONSTERA27', 
        'sub-MONSTERA30', 'sub-MONSTERA34']

todo_subs = list(set(subs) - set(bad))
todo_subs.sort()
print(todo_subs)

for sub in todo_subs:
    file_list = [x for x in glob.glob(opj(preprocess_dir, sub, '*_space-T1w_desc-preproc_bold_trim6TRs_centered-masked*'))] 

    file_list.sort()
    print(file_list)
    
    out_dir = opj(preprocess_dir, '%s' % (sub))

    mask_output = opj(preprocess_dir, sub, '%s_space-T1w_desc-brain_intersect_mask.nii.gz' % (sub))
    avg_mask = nib.load(mask_output)
    affine_mat = avg_mask.affine #should be the same as the epi data
    print(avg_mask.shape)
    
    for f in file_list:
        
        run = os.path.basename(f).split('_')[1]
        print('now on session:', run, 'for', f)
        
        output_name = opj(out_dir,'%s_%s_desc-preproc_bold_trim%d_denoise_z-scored.nii.gz' % (sub, run, n_trunc))
        
        if os.path.exists(output_name): 
            print(f'--------------------file existed for: {sub} {run} {f}. Skipped. --------------------')
            continue
        
        epi_masker= NiftiMasker(mask_img=mask_output,  
                                high_pass=1/filtcutoff, #high pass filter
            standardize=True,  # Are you going to zscore the data across time? 
            t_r=tr, 
            #memory='nilearn_cache',  # Caches the mask in the directory given as a string here so that it is easier to load and retrieve
            memory_level=1,  # How much memory will you cache?
            verbose=1)
        
        # load data and regress out confounds
        epi_data = nib.load(f)
        orig_dimsize=epi_data.header.get_zooms()
        print(orig_dimsize)
        
        tmp = Brain_Data(f)
        spikes = tmp.find_spikes(global_spike_cutoff=outlier_cutoff, diff_spike_cutoff=outlier_cutoff)

        # Making confound table
        csv_files = glob.glob(os.path.join(fmriprerp_dir, sub, 'func', f'*{run}*tsv'))
        if (len(csv_files) != 1):
            print(csv_files)
            print('more than one csv files are found. Please double check.')
            break
        covariates = pd.read_csv(csv_files[0], sep='\t')
        mc = covariates[['trans_x','trans_y','trans_z',
                         'rot_x', 'rot_y', 'rot_z',
                         'framewise_displacement',
                         'a_comp_cor_00', 'a_comp_cor_01','a_comp_cor_02','a_comp_cor_03','a_comp_cor_04','a_comp_cor_05', 
                         'csf']]
        mc['big_fd'] = np.where(mc['framewise_displacement']>0.5, 1, 0)
        mc_trim = mc.iloc[n_trunc: , :].reset_index(drop = True)
        dm_trim = Design_Matrix(pd.concat([mc_trim, spikes.drop(labels='TR', axis=1)], axis=1), sampling_freq=1/tr)
        dm_trim = dm_trim.add_poly(order=2, include_lower=True) # Add Intercept, Linear and Quadratic Trends
        #dm_trim = dm.iloc[n_trunc: , :]
        
        print('transform next...')
        print(type(f))
        epi_mask_data = epi_masker.fit_transform(f,confounds=dm_trim)
        
        coords = np.where(avg_mask.get_fdata())
        bold_vol=[]
        bold_vol=np.zeros((avg_mask.shape[0], avg_mask.shape[1], avg_mask.shape[2], epi_mask_data.shape[0]))
        bold_vol[coords[0], coords[1], coords[2], :] = epi_mask_data.T
        print('epi_mask_data shape:', bold_vol.shape)
        
        bold_nii = nib.Nifti1Image(bold_vol, affine_mat)
        hdr = bold_nii.header  # get a handle for the .nii file's header
        hdr.set_zooms((orig_dimsize[0], orig_dimsize[1], orig_dimsize[2], orig_dimsize[3]))
        nib.save(bold_nii, output_name)
        
        print(f'--------------------{sub} {run} finished denoise and z-score--------------------')
        
