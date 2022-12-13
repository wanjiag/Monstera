import os
from os.path import join as opj

import numpy as np
import nibabel as nib
import glob
#from nilearn.image import mean_img
from nilearn.masking import intersect_masks
from nipype.interfaces.afni import Calc, TStat

session_list = []
for i in range(1,11):
    session_list.append('task-{:02d}'.format(i))
n_trunc = 6
derivative_dir = '/projects/kuhl_lab/wanjiag/MONSTERA/derivatives/'

fmriprep_base_dir = opj(derivative_dir, 'fmriprep/')
f_list = [x for x in glob.glob(os.path.join(fmriprep_base_dir, '*sub-MONSTERA*/'))]
subs = list(map(lambda f: f[len(os.path.commonpath(f_list))+1:-1], f_list))
subs.sort()
print(subs)

for sub in subs:
    print(sub)
    bold_dir=opj(fmriprep_base_dir, '%s/func/' % (sub))

    out_dir = opj(derivative_dir, 'preprocess/%s' % (sub))
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    # Calculate masks intersection    
    print('calculating mask intersection...')
    mask_output = opj(out_dir, '%s_space-T1w_desc-brain_intersect_mask.nii.gz' % (sub))
    if not os.path.exists(mask_output): 
        mask_imgs = [x for x in glob.glob(os.path.join(fmriprep_base_dir, sub, 'func', sub+'_task-*_space-T1w_desc-brain_mask.nii.gz'))] 
        mask_imgs.sort()
        print(mask_imgs)
        overall_mask = intersect_masks(mask_imgs, threshold=1, connected=True)
        overall_mask.to_filename(mask_output)
    else:
        print(f'-------------------- Mask file existed for {sub}. Skipped. --------------------')


    # Trim images

    for run in session_list:
        
        if (sub == 'sub-MONSTERA29' and run == 'task-02'):
            continue
        
        out_file=opj(out_dir, '%s_%s_space-T1w_desc-preproc_bold_trim%dTRs_centered-masked.nii.gz' % (sub, run, n_trunc))
        if os.path.exists(out_file): 
            print(f'-------------------- file existed for: {sub} {run}. Skipped. --------------------')
            continue
        else:
            print('triming data...')
            # T1 space
            func_file = opj(bold_dir, "%s_%s_space-T1w_desc-preproc_bold.nii.gz"% (sub, run))

            epi_data=nib.load(func_file)
            epi=epi_data.get_fdata()
            #truncate
            epi_trunc =np.zeros((epi_data.shape[0], epi_data.shape[1], epi_data.shape[2], epi_data.shape[3]-n_trunc))
            epi_trunc[:, :, :, :] = epi[:,:,:,n_trunc:]

            print(epi_data.shape, '  ', epi_trunc.shape)

            dimsize=epi_data.header.get_zooms()
            print(dimsize)
            orig_dimsize=dimsize

            affine_mat = epi_data.affine  # What is the orientation of the data
            print(affine_mat)

            # Save the volume
            trim_output = opj(out_dir, '%s_%s_space-T1w_desc-preproc_bold_trim%dTRs.nii.gz' % (sub, run, n_trunc))

            bold_nii = nib.Nifti1Image(epi_trunc, affine_mat)
            hdr = bold_nii.header  # get a handle for the .nii file's header
            hdr.set_zooms((dimsize[0], dimsize[1], dimsize[2], dimsize[3]))
            nib.save(bold_nii, trim_output)
            print('triming data...output to %s'%(trim_output))
            
            # Center values
            ## Calculate mean images
            print('calculating mean......')
            #mean_img = mean_img(trim_output, target_affine=None, target_shape=None, verbose=0, n_jobs=1)
            mean_output = opj(out_dir, '%s_%s_space-T1w_desc-preproc_bold_trim%dTRs_mean-img.nii.gz' % (sub, run, n_trunc))
            #mean_img.to_filename(mean_output)
            tstat = TStat()
            tstat.inputs.in_file = trim_output
            tstat.inputs.args = '-mean'
            tstat.inputs.out_file = mean_output
            print(tstat.cmdline)
            res = tstat.run() 
            
            print('calculating mean...output to %s'%(mean_output))

            ## Using AFNI to center and set upper and lower bound
            print('Centering data ......')
            calc = Calc()
            calc.inputs.in_file_a = trim_output
            calc.inputs.in_file_b = mean_output
            calc.inputs.in_file_c = mask_output

            calc.inputs.expr= 'c * min(200, a/b*100)*step(a)*step(b)'
            calc.inputs.out_file = out_file

            print(calc.cmdline)
            calc.run()
            print('Centering data...output to %s'%(out_file))