import pandas as pd
from os.path import join as opj
import os 
from nipype.interfaces import fsl

from glob import glob
from nilearn.input_data import NiftiMasker
from nilearn.masking import intersect_masks

from nipype.interfaces.ants import ApplyTransforms
from nipype.interfaces.afni import TStat
import subprocess

######## Functions ########

def sh(script):
    os.system("bash -c '%s'" % script)
    
    
def mask_rois(in_file, brain_mask, file_name):
    
    mask_out_file = opj(output_dir, '{}_thre_{}_masked.nii.gz'.format(file_name,epi_mask_threshold))
    
    masked = intersect_masks([in_file, brain_mask], threshold=1, connected=False)
    masked.to_filename(mask_out_file)
    
    return mask_out_file
    
def coreg_2_epi(in_file, file_name):
    
    # Coregister any map into the epi space
    flt_out_file = opj(output_dir, '{}.nii.gz'.format(file_name))

    flt = fsl.FLIRT(in_file = in_file,
                    reference = avg_run_file,
                    apply_xfm = True,
                    uses_qform = True,
                    out_matrix_file = opj(output_dir, '{}.mat'.format(file_name)),
                    out_file = flt_out_file
                   )
    print(flt.cmdline)
    flt.run()

    # Threshold the epi space mask so it fits the original mask better and binarizes the mask
    trh_out_file = opj(output_dir, '{}_thre_{}.nii.gz'.format(file_name,epi_mask_threshold))
    trh = fsl.Threshold(thresh = epi_mask_threshold,
                        in_file = flt_out_file,
                        args = '-bin',
                        out_file = trh_out_file
                   )
    print(trh.cmdline)
    trh.run()
    
    masked_out_file = mask_rois(trh_out_file, brain_mask, file_name)
    
    return masked_out_file

def calculate_mean(in_file, file_name):
    ## Calculate mean images
    print('calculating mean......')
    #mean_img = mean_img(trim_output, target_affine=None, target_shape=None, verbose=0, n_jobs=1)
    mean_output = file_name
    #mean_img.to_filename(mean_output)
    tstat = TStat()
    tstat.inputs.in_file = in_file
    tstat.inputs.args = '-mean'
    tstat.inputs.out_file = mean_output
    print(tstat.cmdline)
    res = tstat.run() 

    print('calculating mean...output to %s'%(mean_output))

######## Running ########

derivative_dir = '/projects/kuhl_lab/wanjiag/MONSTERA/derivatives/'
preprocess_base_dir = opj(derivative_dir, 'preprocess/')
fmriprep_base_dir = opj(derivative_dir, 'fmriprep/')
automatic_detecting_subjects = False

if automatic_detecting_subjects:
    f_list = [x for x in glob(os.path.join(fmriprep_base_dir, '*sub-MONSTERA*/'))]
    subs = list(map(lambda f: f[len(os.path.commonpath(f_list))+1:-1], f_list))
    subs.sort()
    print(subs)
else:
    #subs = ['sub-MONSTERA06', 'sub-MONSTERA07', 'sub-MONSTERA08', 'sub-MONSTERA09', 'sub-MONSTERA10']
    #subs = ['sub-MONSTERA11']    
    #subs = ['sub-MONSTERA12', 'sub-MONSTERA13']
    #subs = ['sub-MONSTERA14', 'sub-MONSTERA15','sub-MONSTERA16','sub-MONSTERA17','sub-MONSTERA18']
    #subs = ['sub-MONSTERA19']
    #subs = ['sub-MONSTERA20', 'sub-MONSTERA21']
    #subs = ['sub-MONSTERA22', 'sub-MONSTERA23']
    #subs = ['sub-MONSTERA24', 'sub-MONSTERA25', 'sub-MONSTERA26']
    #subs = ['sub-MONSTERA27', 'sub-MONSTERA28']
    #subs = ['sub-MONSTERA29', 'sub-MONSTERA31', 'sub-MONSTERA32', 'sub-MONSTERA33']
    subs = ['sub-MONSTERA35', 'sub-MONSTERA36', 'sub-MONSTERA37']
    
session_list = []
for i in range(1,11):
    session_list.append('task-{:02d}'.format(i))

epi_mask_threshold = 0.5

for subnum in subs:

    output_dir = opj(derivative_dir, 'rois', subnum)

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    fmriprep_dir = opj(fmriprep_base_dir, subnum)
    preprocess_dir = opj(preprocess_base_dir, subnum)

    print('--------------------{}-------------------'.format(subnum))
    print(output_dir)

    # Getting brain mask
    brain_mask = opj(preprocess_dir, '{}_space-T1w_desc-brain_intersect_mask.nii.gz'.format(subnum))

    # Finding and coverting aparc into nifti file.
    mgz_file = opj(fmriprep_base_dir, 'sourcedata', 'freesurfer', subnum, 'mri', 'aparc.a2009s+aseg.mgz')
    gii_file = opj(output_dir, 'aparc.a2009s+aseg.nii.gz'.format(subnum))
    print(mgz_file)
    print(gii_file)
    p = subprocess.run(['mri_convert', mgz_file, gii_file],stdout=subprocess.PIPE)
    p.stdout 
    
    # Finding and copying aparcaseg file into ROIs folder
    aparc_file = os.path.join(fmriprep_dir,'anat','{}_run-5_desc-aparcaseg_dseg.nii.gz'.format(subnum))
    aparc_output = os.path.join(output_dir, 'run-5_desc-aparcaseg_dseg.nii.gz'.format(subnum))
    print(aparc_file)
    print(aparc_output)
    p = subprocess.run(['cp', aparc_file, aparc_output],stdout=subprocess.PIPE)
    p.stdout 
    
    # Calculate All runs average as a reference image
    avg_run_file = opj(output_dir, 'avg_all_fmriprerp_func.nii.gz')
    if not os.path.exists(avg_run_file): 
        add_string = ''
        for session in session_list:
            
            if (subnum == 'sub-MONSTERA29' and session == 'task-02'):
                continue
            
            in_file = opj(preprocess_dir, '{}_{}_desc-preproc_bold_trim6_denoise_z-scored.nii.gz'.format(subnum, session))
            file_name = opj(output_dir, '{}_{}_desc-preproc_bold_trim6_denoise_z-scored_mean.nii.gz'.format(subnum, session))
            calculate_mean(in_file, file_name)

            if session == session_list[0]:
                continue
            add_string += '-add {} '.format(file_name)

        add_string += '-div {}'.format(len(session_list))
        in_file  = opj(output_dir, '{}_{}_desc-preproc_bold_trim6_denoise_z-scored_mean.nii.gz'.format(subnum, session_list[0]))
        maths = fsl.ImageMaths(in_file=in_file, 
                                op_string=add_string,
                                out_file=avg_run_file)
        print(maths.cmdline)
        maths.run()
        
        sh('rm {}/*desc-preproc_bold_trim6_denoise_z-scored_mean.nii.gz'.format(output_dir))
        
    
    print('--------------------Angular Gyrus-------------------')
    ag = {'ctx_lh_G_pariet_inf-Angular':11125,
          'ctx_rh_G_pariet_inf-Angular':12125}

    for i in ag:
        op_string = '-thr {} -uthr {}'.format(ag[i],ag[i])
        out_file = opj(output_dir, '{}.nii.gz'.format(i))

        maths = fsl.ImageMaths(in_file=gii_file, 
                                op_string=op_string,
                                out_file=out_file)
        print(maths.cmdline)
        maths.run() 
    
    in_file  = opj(output_dir, 'ctx_lh_G_pariet_inf-Angular.nii.gz')
    op_string = '-add {} -bin'.format(opj(output_dir, 'ctx_rh_G_pariet_inf-Angular.nii.gz'))

    out_file = opj(output_dir, 'angular_gyrus.nii.gz'.format(i))
    maths = fsl.ImageMaths(in_file=in_file, 
                            op_string=op_string,
                            out_file=out_file)
    print(maths.cmdline)
    maths.run()
    
    sh('rm {}/ctx_*_G_pariet_inf-Angular.nii.gz'.format(output_dir))
    
    coreg_2_epi(out_file, 'angular_gyrus_2_epi')
    
    # Whole Hippocampus
    print('--------------------Whole Hippocampus-------------------')
    hippo = {'Left-Hippocampus':17,
             'Right-Hippocampus':53}
    for i in hippo:
        op_string = '-thr {} -uthr {}'.format(hippo[i],hippo[i])
        out_file = opj(output_dir, '{}.nii.gz'.format(i))

        maths = fsl.ImageMaths(in_file=aparc_output, 
                                op_string=op_string,
                                out_file=out_file)
        print(maths.cmdline)
        maths.run()

    in_file  = opj(output_dir, 'Left-Hippocampus.nii.gz')
    op_string = '-add {} -bin'.format(opj(output_dir, 'Right-Hippocampus.nii.gz'))

    out_file = opj(output_dir, 'hippocampus.nii.gz'.format(i))
    maths = fsl.ImageMaths(in_file=in_file, 
                            op_string=op_string,
                            out_file=out_file)
    print(maths.cmdline)
    maths.run()

    sh('rm {}/*-Hippocampus.nii.gz'.format(output_dir))
    
    coreg_2_epi(out_file, 'hippocampus_2_epi')
    
    # PPA from MNI space
    print('--------------------PPA-------------------')
    ppa_mni = '/home/wanjiag/projects/MONSTERA/derivatives/rois/mni/ppa/ppa.nii.gz'
    h5 = opj(fmriprep_dir, 'anat/{}_run-5_from-MNI152NLin2009cAsym_to-T1w_mode-image_xfm.h5'.format(subnum))

    print(ppa_mni, '\n', avg_run_file, '\n', h5, '\n', output_dir)
    
    at = ApplyTransforms(input_image = ppa_mni,
                         dimension = 3,
                         reference_image = avg_run_file,
                         float = False,
                         transforms = h5,
                         output_image = opj(output_dir, 'ppa_mni_2_epi.nii.gz')
                        )
    print(at.cmdline)
    command = "module load singularity; singularity exec --bind /projects/kuhl_lab/wanjiag/MONSTERA/derivatives:/projects/kuhl_lab/wanjiag/MONSTERA/derivatives /gpfs/projects/kuhl_lab/shared/containers/fmriprep-21.0.1.simg {}".format(at.cmdline)

    p = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    p.stdout
    
    ppa_output = opj(output_dir, 'ppa_mni_2_epi.nii.gz')
    
    trh_out_file = opj(output_dir, 
                       'ppa_mni_2_epi_thr_{}.nii.gz'.format(epi_mask_threshold))
    trh = fsl.Threshold(thresh = epi_mask_threshold,
                        in_file = ppa_output,
                        args = '-bin',
                        out_file = trh_out_file
                   )
    print(trh.cmdline)
    trh.run()
    
    mask_rois(trh_out_file, brain_mask, 'ppa_mni_2_epi')
    
    # EVC from MNI space
    print('--------------------EVC-------------------')
    ev_mni_path = '/home/wanjiag/projects/MONSTERA/derivatives/rois/mni/visual_cortex/subj_vol_all'
    ev_files = ['perc_VTPM_vol_roi1_lh.nii.gz',
                'perc_VTPM_vol_roi1_rh.nii.gz',
                'perc_VTPM_vol_roi2_lh.nii.gz',
                'perc_VTPM_vol_roi2_rh.nii.gz']

    print(ev_mni_path, '\n', avg_run_file, '\n', h5, '\n', output_dir)
    
    ev_file_threshold = 50
    ev_output = []
    cmdline = []

    for ev_file in ev_files:
        at_out_file = opj(output_dir, '{}_2_epi.nii.gz'.format(ev_file.split('.')[0]))
        at = ApplyTransforms(input_image = opj(ev_mni_path,ev_file),
                             dimension = 3,
                             reference_image = avg_run_file,
                             float = False,
                             transforms = h5,
                             output_image = at_out_file
                            )
        print(at.cmdline)
        command = "module load singularity;singularity exec --bind /projects/kuhl_lab/wanjiag/MONSTERA/derivatives:/projects/kuhl_lab/wanjiag/MONSTERA/derivatives /gpfs/projects/kuhl_lab/shared/containers/fmriprep-21.0.1.simg {}".format(at.cmdline)
        p = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
        p.stdout

        trh_out_file = opj(output_dir, '{}_2_epi_thr_{}.nii.gz'.format(ev_file.split('.')[0], ev_file_threshold))
        trh = fsl.Threshold(thresh = ev_file_threshold,
                            in_file = at_out_file,
                            args = '-bin',
                            out_file = trh_out_file
                       )
        print(trh.cmdline)
        trh.run()

        ev_output.append(trh_out_file)

        
    in_file  = opj(output_dir, ev_output[0])
    ev_add = ev_output[1:]
    op_string = ''

    for ev in ev_add:
        op_string += '-add {} '.format(ev)

    op_string += '-bin'
    out_file = opj(output_dir, 'evc_2_epi_thr_0.5.nii.gz')
    maths = fsl.ImageMaths(in_file=in_file, 
                            op_string=op_string,
                            out_file=out_file)
    print(maths.cmdline)
    maths.run()
    sh('rm {}/perc_VTPM_vol_roi*'.format(output_dir))
    
    mask_rois(out_file, brain_mask, 'evc_2_epi')

