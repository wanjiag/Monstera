import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from glob import glob 
from os.path import join as opj
import os

def summarize(df):
    # remove same round correlations
    df = df.loc[df['round_x'] != df['round_y']]
    #df = df.loc[df['trial_x'] != df['trial_y']]
    
    # define trial type
    conditions = [
    (df['pair_x'] != df['pair_y']),
    (df['destination_x'] != df['destination_y']),
    (df['destination_x'] == df['destination_y'])
    ]
    values = ['across', 'within', 'same']
    df['type'] = np.select(conditions, values)
    
    # define valid type
    conditions = [
    (df['valid_x'] != df['valid_y']),
    (df['valid_x'] == True),
    (df['valid_x'] == False)
        ]
    values = ['valid-invalid', 'valid-valid', 'invalid-invalid']
    df['valid'] = np.select(conditions, values)
    
    return df
    
def group(df, li):
    # mean correlations
    df = df.groupby(li)['cor'].mean().reset_index()
    df['within_trial_TR'] = df['within_trial_TR_x']
    df = df.drop(columns=['within_trial_TR_x'])
    
    return df
    
rois_dict = {
    #'ca23dg-body_thre_0.5_masked':'ca23dg-body',
    #'ca1-body_thre_0.5_masked':'ca1-body',
    #'ca23dg_thre_0.5_masked':'ca23dg',
    #'ca1_thre_0.5_masked':'ca1',
    #'evc_2_epi_thre_0.5_masked':'evc', 
    #'ppa_mni_2_epi_thre_0.5_masked':'ppa',
    'subiculum_thre_0.5_masked': 'sub', 
    'ERC_thre_0.5_masked': 'erc', 
    'PRC_thre_0.5_masked': 'prc',
    'PHC_thre_0.5_masked': 'phc',
}

output_dir = "/home/wanjiag/projects/MONSTERA/derivatives/csv_files/python/"
processed_subs = os.listdir(output_dir)

summary_dir = "/home/wanjiag/projects/MONSTERA/derivatives/csv_files/python_summary/"
processed_subs = os.listdir(output_dir)

file_dir = []

for k,roi in rois_dict.items():
    print(roi)
    file_dir = glob(opj(output_dir, '*', 'sub-MONSTERA*_rolling3_{}.csv'.format(roi)))
    print(len(file_dir))
    df = pd.concat((pd.read_csv(f) for f in file_dir), ignore_index=True)

    output_df = summarize(df)
    
    summary_df = group(output_df, ['sub_x','type','valid','within_trial_TR_x'])
    summary_df['roi'] = roi
    os.makedirs(opj(summary_dir, roi), exist_ok=True) 
    summary_df.to_csv(opj(summary_dir, roi, '{}_rolling3_summary.csv'.format(roi)), index=False) 

    summary_df = group(output_df, ['sub_x','type','valid','within_trial_TR_x', 'round_x', 'round_y'])
    summary_df['roi'] = roi
    summary_df.to_csv(opj(summary_dir, roi, '{}_rolling3_summary_with_rounds.csv'.format(roi)), index=False) 

    summary_df = group(output_df, ['sub_x','type','valid','within_trial_TR_x', 'pair_x', 'pair_y', 'destination_x', 'destination_y'])
    summary_df['roi'] = roi
    summary_df.to_csv(opj(summary_dir, roi, '{}_rolling3_summary_with_destination.csv'.format(roi)), index=False) 
   
    summary_df = group(output_df, ['sub_x','type','valid','within_trial_TR_x', 'pair_x', 'pair_y', 'round_x', 'round_y'])
    summary_df['roi'] = roi
    summary_df.to_csv(opj(summary_dir, roi, '{}_rolling3_summary_with_pairs_and_rounds.csv'.format(roi)), index=False) 

    
    
'''
for k,roi in rois_dict.items():
    print(roi)
    file_dir = glob(opj(output_dir, '*', 'sub-MONSTERA*_norolling_{}.csv'.format(roi)))
    print(len(file_dir))
    df = pd.concat((pd.read_csv(f) for f in file_dir), ignore_index=True)

    output_df = summarize(df)
    
    summary_df = group(output_df, ['sub_x','type','valid','within_trial_TR_x'])
    summary_df['roi'] = roi
    os.makedirs(opj(summary_dir, roi), exist_ok=True) 
    summary_df.to_csv(opj(summary_dir, roi, '{}_norolling_summary.csv'.format(roi)), index=False) 

    summary_df = group(output_df, ['sub_x','type','valid','within_trial_TR_x', 'round_x', 'round_y'])
    summary_df['roi'] = roi
    summary_df.to_csv(opj(summary_dir, roi, '{}_norolling_summary_with_rounds.csv'.format(roi)), index=False) 

    summary_df = group(output_df, ['sub_x','type','valid','within_trial_TR_x', 'pair_x', 'pair_y', 'destination_x', 'destination_y'])
    summary_df['roi'] = roi
    summary_df.to_csv(opj(summary_dir, roi, '{}_norolling_summary_with_destination.csv'.format(roi)), index=False) 
'''
