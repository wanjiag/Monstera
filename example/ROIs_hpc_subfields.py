from nipype.interfaces import fsl
from os.path import join as opj
import os

subfields = {'ca1':1,
             'ca23dg':[2,4] #choosing 2 to 4, including ca2, dg, and ca3
            }

#sublist = ['01','02','03','04','05','06','07',
#           '09','10','11','12','13','14',
#           '17','18','19','20','21',
#           '23','24','25','26','27','28','29',
#           '31','32','33','35','36']

sublist = ['06','22']

# first num = Starting slices in ITK-snap; second num = how many slices to include (inclusive of the last one)

left_body = {'01':[30,10],
            }

right_body = {'01':[30,10]
             }


def coreg_2_epi(in_file, ref_file, file_name, final_output):
    
    ## Coregister the hippocampus map into the epi space
    flt_out_file = opj(final_output, '{}.nii.gz'.format(file_name))

    flt = fsl.FLIRT(in_file = in_file,
                    reference = ref_file,
                    apply_xfm = True,
                    uses_qform = True,
                    out_matrix_file = opj(final_output, '{}.mat'.format(file_name)),
                    out_file = flt_out_file
                   )
    print(flt.cmdline)
    flt.run()

    ## Threshold the epi space mask so it fits the original mask better and binarizes the mask
    trh_out_file = opj(final_output, '{}_thre_{}.nii.gz'.format(file_name,epi_mask_threshold))
    trh = fsl.Threshold(thresh = epi_mask_threshold,
                        in_file = flt_out_file,
                        args = '-bin',
                        out_file = trh_out_file
                   )
    print(trh.cmdline)
    trh.run()
    
    return trh_out_file

#fslroi sub-01_left_lfseg_corr_nogray.nii.gz test.nii.gz 0 -1 0 -1 34 9
def hippo_body(left, right, subnum, output_dir):
    
    left_output = opj(output_dir, 'sub-{}_left_body_nogray.nii.gz'.format(subnum))
    roi = fsl.ExtractROI(in_file = left, z_min=(left_body[subnum][0]-1), z_size=left_body[subnum][1], 
                         x_min = 0, x_size = -1, y_min = 0, y_size = -1,
                         roi_file = left_output)
    print(roi.cmdline)
    roi.run()
    
    front = left_body[subnum][0]-1-1
    end = 65-front-left_body[subnum][1]
    empty = '/home/wanjiag/projects/NEUDIF/bids_data/derivatives/ashs/empty_t2.nii.gz'
    
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
    
    left_t2 = opj(output_dir, 'sub-{}_left_body_nogray.nii.gz'.format(subnum))
    merge = fsl.Merge(in_files = [front_empty, left_output, end_empty],
                     dimension = 'z',
                     merged_file = left_t2)
    merge.run()
    
    right_output = opj(output_dir, 'sub-{}_right_body_nogray.nii.gz'.format(subnum))
    roi = fsl.ExtractROI(in_file = right, z_min=(right_body[subnum][0]-1), z_size=right_body[subnum][1], 
                         x_min = 0, x_size = -1, y_min = 0, y_size = -1,
                         roi_file = right_output)
    print(roi.cmdline)    
    roi.run()
    
    front = right_body[subnum][0]-1-1
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
    
    right_t2 = opj(output_dir, 'sub-{}_right_body_nogray.nii.gz'.format(subnum))
    merge = fsl.Merge(in_files = [front_empty, right_output, end_empty],
                     dimension = 'z',
                     merged_file = right_t2)
    merge.run()
    
    return left_t2, right_t2
    

################# Whole hippocampus ###################

epi_mask_threshold = 0.5

for subnum in sublist:

    print('---------------------Whole hippocampus: sub{}----------------------'.format(subnum))

    ashs = '/home/wanjiag/projects/NEUDIF/bids_data/derivatives/ashs/sub-{}'.format(subnum)

    left = opj(ashs, 'final/sub-{}_left_lfseg_corr_nogray.nii.gz'.format(subnum))
    right = opj(ashs, 'final/sub-{}_right_lfseg_corr_nogray.nii.gz'.format(subnum))
    
    output_dir = '/home/wanjiag/projects/NEUDIF/bids_data/derivatives/ashs/sub-{}/final/binary'.format(subnum)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
        
    # coreg T2 to T1 for the mat file
    T2_to_T1_mat = opj(output_dir, 'T2_to_T1.mat')
    T1 = '/home/wanjiag/projects/NEUDIF/bids_data/derivatives/fmriprep/sub-{}/anat/sub-{}_desc-preproc_T1w.nii.gz'.format(subnum, subnum)
    flt = fsl.FLIRT(in_file = '/home/wanjiag/projects/NEUDIF/bids_data/sub-{}/anat/sub-{}_T2w.nii.gz'.format(subnum, subnum),
                    reference = T1,
                    out_file = opj(output_dir, 'T2_to_T1.nii.gz'),
                    out_matrix_file = T2_to_T1_mat,
                    dof = 6,
                    cost = 'mutualinfo')
    print(flt.cmdline)
    flt.run()
    
    for i in subfields:
        if i == 'ca1':
            op_string = '-thr {} -uthr {} -bin'.format(subfields[i],subfields[i])
        if i == 'ca23dg':
            op_string = '-thr {} -uthr {} -bin'.format(subfields[i][0],subfields[i][1])
                
        left_out_file = opj(output_dir, 'sub-{}_left_{}.nii.gz'.format(subnum, i))
        maths = fsl.ImageMaths(in_file=left, 
                                op_string=op_string,
                                out_file=left_out_file)
        print(maths.cmdline)
        maths.run()
        
        right_out_file = opj(output_dir, 'sub-{}_right_{}.nii.gz'.format(subnum, i))
        maths = fsl.ImageMaths(in_file=right, 
                                op_string=op_string,
                                out_file=right_out_file)
        print(maths.cmdline)
        maths.run()
        
        in_file  = left_out_file
        out_file = opj(output_dir, 'sub-{}_{}.nii.gz'.format(subnum, i))
        add_string = '-add {}'.format(right_out_file)
        maths = fsl.ImageMaths(in_file=in_file, 
                                op_string=add_string,
                                out_file=out_file)
        print(maths.cmdline)
        maths.run()
        
        out_file_in_t1 = opj(output_dir, '{}_2_t1.nii.gz'.format(i))
        flt = fsl.FLIRT(in_file = out_file,
                        reference = T1,
                        apply_xfm = True,
                        in_matrix_file = T2_to_T1_mat,
                        out_matrix_file = opj(output_dir, '{}_2_t1.mat'.format(i)),
                        out_file = out_file_in_t1
                        )
        print(flt.cmdline)
        flt.run()
        
        ref_file = '/home/wanjiag/projects/NEUDIF/bids_data/derivatives/1st_level/combine_repeat/sub-{}/run_avg/sub-{}_avg_all.nii.gz'.format(subnum,subnum)
        roi_output = '/home/wanjiag/projects/NEUDIF/bids_data/derivatives/1st_level/rois/sub-{}'.format(subnum)
        coreg_2_epi(out_file_in_t1, ref_file, i, roi_output)
        

################## Hippocampus Body #################

epi_mask_threshold = 0.5

for subnum in sublist:

    print('---------------------Hippocampus body: sub{}----------------------'.format(subnum))

    ashs = '/home/wanjiag/projects/NEUDIF/bids_data/derivatives/ashs/sub-{}'.format(subnum)

    left = opj(ashs, 'final/sub-{}_left_lfseg_corr_nogray.nii.gz'.format(subnum))
    right = opj(ashs, 'final/sub-{}_right_lfseg_corr_nogray.nii.gz'.format(subnum))

    output_dir = '/home/wanjiag/projects/NEUDIF/bids_data/derivatives/ashs/sub-{}/final/binary'.format(subnum)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)    
    
    left, right = hippo_body(left, right, subnum, output_dir)

    # coreg T2 to T1 for the mat file
    T2_to_T1_mat = opj(output_dir, 'T2_to_T1.mat')
    T1 = '/home/wanjiag/projects/NEUDIF/bids_data/derivatives/fmriprep/sub-{}/anat/sub-{}_desc-preproc_T1w.nii.gz'.format(subnum, subnum)
    flt = fsl.FLIRT(in_file = '/home/wanjiag/projects/NEUDIF/bids_data/sub-{}/anat/sub-{}_T2w.nii.gz'.format(subnum, subnum),
                    reference = T1,
                    out_file = opj(output_dir, 'T2_to_T1.nii.gz'),
                    out_matrix_file = T2_to_T1_mat,
                    dof = 6,
                    cost = 'mutualinfo')
    print(flt.cmdline)
    flt.run()

    for i in subfields:
        if i == 'ca1':
            op_string = '-thr {} -uthr {} -bin'.format(subfields[i],subfields[i])
        if i == 'ca23dg':
            op_string = '-thr {} -uthr {} -bin'.format(subfields[i][0],subfields[i][1])
            
        left_out_file = opj(output_dir, 'sub-{}_left_{}_body.nii.gz'.format(subnum, i))
        maths = fsl.ImageMaths(in_file=left, 
                                op_string=op_string,
                                out_file=left_out_file)
        print(maths.cmdline)
        maths.run()
        
        right_out_file = opj(output_dir, 'sub-{}_right_{}_body.nii.gz'.format(subnum, i))
        maths = fsl.ImageMaths(in_file=right, 
                                op_string=op_string,
                                out_file=right_out_file)
        print(maths.cmdline)
        maths.run()
        
        in_file  = left_out_file
        out_file = opj(output_dir, 'sub-{}_{}_body.nii.gz'.format(subnum, i))
        add_string = '-add {}'.format(right_out_file)
        maths = fsl.ImageMaths(in_file=in_file, 
                                op_string=add_string,
                                out_file=out_file)
        print(maths.cmdline)
        maths.run()
        
        out_file_in_t1 = opj(output_dir, '{}_2_t1_body.nii.gz'.format(i))
        flt = fsl.FLIRT(in_file = out_file,
                        reference = T1,
                        apply_xfm = True,
                        in_matrix_file = T2_to_T1_mat,
                        out_matrix_file = opj(output_dir, '{}_2_t1_body.mat'.format(i)),
                        out_file = out_file_in_t1
                        )
        print(flt.cmdline)
        flt.run()                

        ref_file = '/home/wanjiag/projects/NEUDIF/bids_data/derivatives/1st_level/combine_repeat/sub-{}/run_avg/sub-{}_avg_all.nii.gz'.format(subnum,subnum)        
        roi_output = '/home/wanjiag/projects/NEUDIF/bids_data/derivatives/1st_level/rois/sub-{}'.format(subnum)
        coreg_2_epi(out_file_in_t1, ref_file, i+'_body', roi_output)
