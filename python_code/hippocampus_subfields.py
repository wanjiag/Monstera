from nipype.interfaces import fsl
from nilearn.masking import intersect_masks
from os.path import join as opj
import os

subfields = {'ca1':1,
             'ca23dg':[2,4] #choosing 2 to 4, including ca2, dg, and ca3
            }

#sub_list = ['sub-MONSTERA06', 'sub-MONSTERA07', 'sub-MONSTERA08', 'sub-MONSTERA09', 'sub-MONSTERA10']
#sub_list = ['sub-MONSTERA11']
#sub_list = ['sub-MONSTERA14','sub-MONSTERA15','sub-MONSTERA16','sub-MONSTERA17','sub-MONSTERA18']
#sub_list = ['sub-MONSTERA19']
#sub_list = ['sub-MONSTERA20', 'sub-MONSTERA21']
#sub_list = ['sub-MONSTERA22', 'sub-MONSTERA23']
#sub_list = ['sub-MONSTERA24', 'sub-MONSTERA25', 'sub-MONSTERA26']
#sub_list = ['sub-MONSTERA27', 'sub-MONSTERA28']
#sub_list = ['sub-MONSTERA29', 'sub-MONSTERA31', 'sub-MONSTERA32', 'sub-MONSTERA33']
#sub_list = ['sub-MONSTERA35', 'sub-MONSTERA36', 'sub-MONSTERA37']
#sub_list = ['sub-MONSTERA38']
#sub_list = ['sub-MONSTERA39']
sub_list = ['sub-MONSTERA40','sub-MONSTERA41','sub-MONSTERA42','sub-MONSTERA43']


# first num = Starting slices in ITK-snap; second num = how many slices to include (inclusive of the last one)

left_body = {#'01':[30,10],
             'sub-MONSTERA06':[34,8],
             'sub-MONSTERA07':[31,10],
             'sub-MONSTERA08':[30,10],
             'sub-MONSTERA09':[32,10],
             'sub-MONSTERA10':[31,11],
             'sub-MONSTERA11':[31,11],
             'sub-MONSTERA12':[31,10],
             'sub-MONSTERA13':[34,9],
             'sub-MONSTERA14':[33,11],
             'sub-MONSTERA15':[30,10],
             'sub-MONSTERA16':[31,11],
             'sub-MONSTERA17':[31,11],
             'sub-MONSTERA18':[31,8],
             'sub-MONSTERA19':[33,9],
             'sub-MONSTERA20':[31,9],
             'sub-MONSTERA21':[33,10],
             'sub-MONSTERA22':[31,10],
             'sub-MONSTERA23':[31,10],
             'sub-MONSTERA24':[34,11],
             'sub-MONSTERA25':[31,9],
             'sub-MONSTERA26':[29,9],
             'sub-MONSTERA27':[31,9],
             'sub-MONSTERA28':[32,12],
             'sub-MONSTERA29':[35,8],
             'sub-MONSTERA31':[33,9],
             'sub-MONSTERA32':[33,12],
             'sub-MONSTERA33':[33,11],
             'sub-MONSTERA35':[33,8],
             'sub-MONSTERA36':[33,9],
             'sub-MONSTERA37':[33,9],
             'sub-MONSTERA38':[32,12],
             'sub-MONSTERA39':[33,9],
             'sub-MONSTERA40':[32,11],
             'sub-MONSTERA41':[32,9],
             'sub-MONSTERA42':[34,10],
             'sub-MONSTERA43':[32,10]}

right_body = {#'01':[30,10],
              'sub-MONSTERA06':[31,11],
              'sub-MONSTERA07':[32,9],
              'sub-MONSTERA08':[30,10],
              'sub-MONSTERA09':[32,10],
              'sub-MONSTERA10':[31,11],
              'sub-MONSTERA11':[29,13],
              'sub-MONSTERA12':[30,11],
              'sub-MONSTERA13':[33,10],
              'sub-MONSTERA14':[34,10],
              'sub-MONSTERA15':[30,10],
              'sub-MONSTERA16':[31,11],
              'sub-MONSTERA17':[30,12],
              'sub-MONSTERA18':[30,9],
              'sub-MONSTERA19':[31,11],             
              'sub-MONSTERA20':[31,10],
              'sub-MONSTERA21':[31,12],
              'sub-MONSTERA22':[30,11],
              'sub-MONSTERA23':[32,9],
              'sub-MONSTERA24':[34,11],
              'sub-MONSTERA25':[31,9],
              'sub-MONSTERA26':[29,9],
              'sub-MONSTERA27':[30,10],
              'sub-MONSTERA28':[32,12],
              'sub-MONSTERA29':[34,9],
              'sub-MONSTERA31':[32,10],
              'sub-MONSTERA32':[34,11],
              'sub-MONSTERA33':[32,12],
              'sub-MONSTERA35':[30,11],
              'sub-MONSTERA36':[32,10],
              'sub-MONSTERA37':[32,10],
              'sub-MONSTERA38':[32,12],
              'sub-MONSTERA39':[33,9],
              'sub-MONSTERA40':[33,10],
              'sub-MONSTERA41':[32,9],
              'sub-MONSTERA42':[34,10],
              'sub-MONSTERA43':[33,9]}


epi_mask_threshold = 0.5

def mask_rois(in_file, brain_mask, file_name):
    
    mask_out_file = opj(output_dir, '{}_thre_{}_masked.nii.gz'.format(file_name,epi_mask_threshold))
    
    masked = intersect_masks([in_file, brain_mask], threshold=1, connected=False)
    masked.to_filename(mask_out_file)
    
    return mask_out_file

def coreg_2_epi(in_file, ref_file, file_name, final_output):
    
    ## Coregister the hippocampus map into the epi space
    flt_out_file = opj(final_output, '{}_epi-space.nii.gz'.format(file_name))

    flt = fsl.FLIRT(in_file = in_file,
                    reference = ref_file,
                    apply_xfm = True,
                    uses_qform = True,
                    out_matrix_file = opj(final_output, '{}_epi-space.mat'.format(file_name)),
                    out_file = flt_out_file
                   )
    print(flt.cmdline)
    flt.run()

    ## Threshold the epi space mask so it fits the original mask better and binarizes the mask
    trh_out_file = opj(final_output, '{}_epi-space_thre_{}.nii.gz'.format(file_name,epi_mask_threshold))
    trh = fsl.Threshold(thresh = epi_mask_threshold,
                        in_file = flt_out_file,
                        args = '-bin',
                        out_file = trh_out_file
                   )
    print(trh.cmdline)
    trh.run()
    
    masked_out_file = mask_rois(trh_out_file, brain_mask, file_name)
    
    return masked_out_file


def hippo_body(left, right, subnum, output_dir):
    
    left_output = opj(output_dir, '{}_left_body_nogray.nii.gz'.format(subnum))
    roi = fsl.ExtractROI(in_file = left, z_min=(left_body[subnum][0]), z_size=left_body[subnum][1], 
                         x_min = 0, x_size = -1, y_min = 0, y_size = -1,
                         roi_file = left_output)
    print(roi.cmdline)
    roi.run()
    
    front = left_body[subnum][0]-1
    end = 65-front-left_body[subnum][1]
    empty = '/home/wanjiag/projects/MONSTERA/derivatives/rois/ASHS/empty_t2.nii.gz'
    
    front_empty = opj(output_dir, 'front_empty.nii.gz')
    roi = fsl.ExtractROI(in_file = empty, z_min=0, z_size=front, 
                         x_min = 0, x_size = -1, y_min = 0, y_size = -1,
                         roi_file = front_empty)
    print(roi.cmdline)
    roi.run()
    
    end_empty = opj(output_dir, 'end_empty.nii.gz')
    roi = fsl.ExtractROI(in_file = empty, z_min=0, z_size=end, 
                         x_min = 0, x_size = -1, y_min = 0, y_size = -1,
                         roi_file = end_empty)
    print(roi.cmdline)
    roi.run()
    
    left_t2 = opj(output_dir, '{}_left_body_nogray.nii.gz'.format(subnum))
    merge = fsl.Merge(in_files = [front_empty, left_output, end_empty],
                     dimension = 'z',
                     merged_file = left_t2)
    merge.run()
    
    right_output = opj(output_dir, '{}_right_body_nogray.nii.gz'.format(subnum))
    roi = fsl.ExtractROI(in_file = right, z_min=(right_body[subnum][0]), z_size=right_body[subnum][1], 
                         x_min = 0, x_size = -1, y_min = 0, y_size = -1,
                         roi_file = right_output)
    print(roi.cmdline)    
    roi.run()
    
    front = right_body[subnum][0]-1
    end = 65-front-right_body[subnum][1]
    
    front_empty = opj(output_dir, 'front_empty.nii.gz')
    roi = fsl.ExtractROI(in_file = empty, z_min=0, z_size=front, 
                         x_min = 0, x_size = -1, y_min = 0, y_size = -1,
                         roi_file = front_empty)
    print(roi.cmdline)
    roi.run()
    
    end_empty = opj(output_dir, 'end_empty.nii.gz')
    roi = fsl.ExtractROI(in_file = empty, z_min=0, z_size=end, 
                         x_min = 0, x_size = -1, y_min = 0, y_size = -1,
                         roi_file = end_empty)
    print(roi.cmdline)
    roi.run()
    
    right_t2 = opj(output_dir, '{}_right_body_nogray.nii.gz'.format(subnum))
    merge = fsl.Merge(in_files = [front_empty, right_output, end_empty],
                     dimension = 'z',
                     merged_file = right_t2)
    merge.run()
    
    return left_t2, right_t2

################## Hippocampus Body #################

for subnum in sub_list:
    
    # Getting brain mask
    brain_mask = opj('/home/wanjiag/projects/MONSTERA/derivatives/preprocess/',subnum, '{}_space-T1w_desc-brain_intersect_mask.nii.gz'.format(subnum))
    
    ashs_output_dir = '/home/wanjiag/projects/MONSTERA/derivatives/rois/ASHS/{}'.format(subnum)

    left = opj(ashs_output_dir, 'final/{}_left_lfseg_corr_nogray.nii.gz'.format(subnum))
    right = opj(ashs_output_dir, 'final/{}_right_lfseg_corr_nogray.nii.gz'.format(subnum))
    
    ref_file = '/home/wanjiag/projects/MONSTERA/derivatives/rois/{}/avg_all_fmriprerp_func.nii.gz'.format(subnum) 

    output_base_dir = '/home/wanjiag/projects/MONSTERA/derivatives/rois/{}/ashs/'.format(subnum)
    if not os.path.isdir(output_base_dir):
        os.makedirs(output_base_dir)   
        
    # coreg T2 to T1 for the mat file
    T2_to_T1_mat = opj(output_base_dir, 'T2_to_T1.mat')
    T1 = '/home/wanjiag/projects/MONSTERA/derivatives/fmriprep/{}/anat/{}_run-5_desc-preproc_T1w.nii.gz'.format(subnum, subnum)
    flt = fsl.FLIRT(in_file = '/home/wanjiag/projects/MONSTERA/derivatives/rois/ASHS/{}/tse.nii.gz'.format(subnum),
                    reference = T1,
                    out_file = opj(output_base_dir, 'T2_to_T1.nii.gz'),
                    out_matrix_file = T2_to_T1_mat,
                    dof = 6,
                    cost = 'mutualinfo')
    print(flt.cmdline)
    flt.run()
    
    print('---------------------Whole hippocampus: {}----------------------'.format(subnum))

    output_dir = '/home/wanjiag/projects/MONSTERA/derivatives/rois/{}/ashs/whole'.format(subnum)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)  
        
    for i in subfields:
        if i == 'ca1':
            op_string = '-thr {} -uthr {} -bin'.format(subfields[i],subfields[i])
        if i == 'ca23dg':
            op_string = '-thr {} -uthr {} -bin'.format(subfields[i][0],subfields[i][1])
                
        left_out_file = opj(output_dir, 'left-{}_T2w-space.nii.gz'.format(i))
        maths = fsl.ImageMaths(in_file=left, 
                                op_string=op_string,
                                out_file=left_out_file)
        print(maths.cmdline)
        maths.run()
        
        right_out_file = opj(output_dir, 'right-{}_T2w-space.nii.gz'.format(i))
        maths = fsl.ImageMaths(in_file=right, 
                                op_string=op_string,
                                out_file=right_out_file)
        print(maths.cmdline)
        maths.run()
        
        in_file  = left_out_file
        out_file = opj(output_dir, '{}_T2w-space.nii.gz'.format(i))
        add_string = '-add {}'.format(right_out_file)
        maths = fsl.ImageMaths(in_file=in_file, 
                                op_string=add_string,
                                out_file=out_file)
        print(maths.cmdline)
        maths.run()
        
        out_file_in_t1 = opj(output_dir, '{}_T2w-to-T1-space.nii.gz'.format(i))
        flt = fsl.FLIRT(in_file = out_file,
                        reference = T1,
                        apply_xfm = True,
                        in_matrix_file = T2_to_T1_mat,
                        out_matrix_file = opj(output_dir, '{}_T2w-to-T1-space.mat'.format(i)),
                        out_file = out_file_in_t1
                        )
        print(flt.cmdline)
        flt.run()
        
               
        coreg_2_epi(out_file_in_t1, ref_file, i, output_dir)    

    print('---------------------Hippocampus body: {}----------------------'.format(subnum))

    output_dir = '/home/wanjiag/projects/MONSTERA/derivatives/rois/{}/ashs/body'.format(subnum)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)    
    
    left, right = hippo_body(left, right, subnum, output_dir)

    for i in subfields:
        if i == 'ca1':
            op_string = '-thr {} -uthr {} -bin'.format(subfields[i],subfields[i])
        if i == 'ca23dg':
            op_string = '-thr {} -uthr {} -bin'.format(subfields[i][0],subfields[i][1])
            
        left_out_file = opj(output_dir, 'left-{}-body_T2w-space.nii.gz'.format(i))
        maths = fsl.ImageMaths(in_file=left, 
                                op_string=op_string,
                                out_file=left_out_file)
        print(maths.cmdline)
        maths.run()
        
        right_out_file = opj(output_dir, 'right-{}-body_T2w-space.nii.gz'.format(i))
        maths = fsl.ImageMaths(in_file=right, 
                                op_string=op_string,
                                out_file=right_out_file)
        print(maths.cmdline)
        maths.run()
        
        in_file  = left_out_file
        out_file = opj(output_dir, '{}-body_T2w-space.nii.gz'.format(i))
        add_string = '-add {}'.format(right_out_file)
        maths = fsl.ImageMaths(in_file=in_file, 
                                op_string=add_string,
                                out_file=out_file)
        print(maths.cmdline)
        maths.run()
        
        out_file_in_t1 = opj(output_dir, '{}-body_T2w-to-T1-space.nii.gz'.format(i))
        flt = fsl.FLIRT(in_file = out_file,
                        reference = T1,
                        apply_xfm = True,
                        in_matrix_file = T2_to_T1_mat,
                        out_matrix_file = opj(output_dir, '{}-body_T2w-to-T1-space.mat'.format(i)),
                        out_file = out_file_in_t1
                        )
        print(flt.cmdline)
        flt.run()                

        coreg_2_epi(out_file_in_t1, ref_file, i+'-body', output_dir)
        
