import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from glob import glob 
from os.path import join as opj
import os

def cleaning(df):
    '''
    clearning up files for conditions
    '''
    
    df['n_pic'] = df['npic'].str.split('_', expand=True)[[0]]
    df['TR'] = df['onset'].apply(np.floor).astype('int')
    
    tmp = df['condition'].str.split('/', expand=True)
    
    df['pair'] = tmp[[0]].squeeze().str.extract('(\w+)')
    
    tmp1 = tmp[[1]].squeeze().str.split(',', expand=True)
    df['destination'] = tmp1[[0]].squeeze().str.extract('(\w+)')
    df['valid'] = pd.to_numeric(tmp1[[1]].squeeze(), errors='coerce').apply(lambda x: {0: True, 1: False}.get(x, None))
    df['catch'] = tmp1[[3]].squeeze().notnull()
    
    def segment(x):
        if x <= 25:
            return 'same'
        elif x <= 75:
            return 'similar'
        elif x <= 100:
            return 'different'
        else:
            return None

    df['n_int'] = pd.to_numeric(df['npic'], errors='coerce')
    df['segment'] = df['n_int'].apply(segment)
    
    return df

def cleaning2(df):
    '''
    remove duplicated lines for multiple pictures
    only save one line per second
    '''
    
    df = df.loc[df['catch'] == False]
    df = df.loc[df['segment'].notnull()]
    df = df.drop(columns=['onset', 'design_onset', 'design_end', 'n_pic', 'npic', 'condition', 'n_int', 'catch'])
    
    df = df.drop_duplicates()
    df['within_trial_TR'] = df.groupby(['sub','round','trial'])['TR'].rank(method = 'dense').astype('int')
    #df['odd_even'] = df['round'].apply(lambda x: 'even' if x%2 == 0 else 'odd')
    
    df['round'] = df['round'].astype('int')
    df['trial'] = df['trial'].astype('int')

    return df

def cleaning3(fmri_df):
    '''
    quick cleaning fMRI dataframe
    '''
    fmri_df.rename(columns={'Unnamed: 0':'TR'}, inplace=True)
    fmri_df['round'] = fmri_df['run'].squeeze().str.extract('(\d+)').astype('int')
    fmri_df['sub'] = fmri_df['sub'].squeeze().str.extract('(\d+)').astype('int')
    fmri_df = fmri_df.drop(columns=['run', 'roi'])
    return fmri_df

def pairwise_correlation(curr_tr_df):
    properties = curr_tr_df.iloc[:, :9]
    # calculate correlation for every trial combination
    corr_df = curr_tr_df.T.iloc[9:].astype(float).corr() 
    # taking only the upper triangle of the correlation matrix
    corr_df = corr_df.where(np.triu(np.ones(corr_df.shape)).astype(np.bool))
    # reorganize into long format
    corr_df = corr_df.stack().reset_index()
    # rename columns
    corr_df.columns = ['x', 'y', 'cor']
    overall_df = corr_df.merge(properties, right_index=True, left_on = 'x', how='left').merge(properties, right_index=True, left_on = 'y', how='left')

    return overall_df

def per_tr_calculation(df):
    outputs = []
    trs = df['within_trial_TR'].unique()
    for curr_tr in trs:

        curr_tr_df = df.loc[df['within_trial_TR'] == curr_tr]
        curr_tr_output = pairwise_correlation(curr_tr_df)
        outputs.append(curr_tr_output)

    output_df = pd.concat(outputs)
    output_df['roi'] = roi
    
    return output_df

def save_file(subnum, output_df, file_name):
    sub_out_dir = opj(output_dir, 'sub-MONSTERA{}'.format(subnum))
    if not os.path.isdir(sub_out_dir):
        os.makedirs(sub_out_dir)
    
    out_file = opj(sub_out_dir, file_name)
    output_df.to_csv(out_file, index=False)

def summarize(df):
    # remove same round correlations
    df = df.loc[df['round_x'] != df['round_y']]
    
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
    
    # mean correlations
    df = df.groupby(['type','valid','within_trial_TR_x'])['cor'].mean().reset_index()
    df['within_trial_TR'] = df['within_trial_TR_x']
    df = df.drop(columns=['within_trial_TR_x'])
    
    return df
    
rois_dict = {
    'ca23dg-body_thre_0.5_masked':'ca23dg-body',
    'ca1-body_thre_0.5_masked':'ca1-body',
    'ca23dg_thre_0.5_masked':'ca23dg',
    'ca1_thre_0.5_masked':'ca1', 
    'evc_2_epi_thre_0.5_masked':'evc', 
    'ppa_mni_2_epi_thre_0.5_masked':'ppa'
}

fMRI_dir = "/home/wanjiag/projects/MONSTERA/derivatives/csv_files/fMRI/"
all_subs = os.listdir(fMRI_dir)

output_dir = "/home/wanjiag/projects/MONSTERA/derivatives/csv_files/python/"
processed_subs = os.listdir(output_dir)

todo_subs = list(set(all_subs) - set(processed_subs))
todo_subs.remove('sub-MONSTERA14')

behav_dir = "/home/wanjiag/projects/MONSTERA/derivatives/csv_files/behavior/"
sub_dir = os.listdir(behav_dir)

behav_subnums = [x[-2:] for x in sub_dir]
todo_subnums = [x[-2:] for x in todo_subs]

todo_subnums = list(set(behav_subnums) & set(todo_subnums))

print(todo_subnums)

for subnum in todo_subnums:
    print('---{}---'.format(subnum))
    
    behav_file_dir = opj(behav_dir, 'sub{}'.format(subnum))
    behav_files = glob(opj(behav_file_dir, 'sub*_scan*_timing_*'))
    
    org_behav_df = pd.concat((pd.read_csv(f) for f in behav_files), ignore_index=True)
    behav_df_tmp = cleaning(org_behav_df)
    behav_df = cleaning2(behav_df_tmp)
    
    fmri_file_dir = opj(fMRI_dir, 'sub-MONSTERA{}'.format(subnum))
    for roi_file_name, roi in rois_dict.items():
        print(roi_file_name)
        fmri_files = glob(opj(fmri_file_dir, '{}*'.format(roi_file_name)))
        fmri_files.sort()
        
        fmri_df = pd.concat((pd.read_csv(f) for f in fmri_files), ignore_index=True)
        fmri_df = cleaning3(fmri_df)
        
        # calculating no rolling data
        df = behav_df.merge(fmri_df, on=['sub', 'round', 'TR'], how='left')
        output_df = per_tr_calculation(df)
        save_file(subnum, output_df, 'sub-MONSTERA{}_norolling_{}.csv'.format(subnum, roi))
        
        summary_df = summarize(output_df)
        summary_df['sub'] = subnum
        summary_df['roi'] = roi
        save_file(subnum, summary_df, 'sub-MONSTERA{}_norolling_{}_summary.csv'.format(subnum, roi))
        
        #calculating rolling data
        rolling_df = fmri_df.groupby(['sub','round']).rolling(3, center = True, method = 'table').mean()
        rolling_df = rolling_df.drop(columns= ['sub','round']).reset_index().drop(columns= 'level_2')
        df = behav_df.merge(rolling_df, on=['sub', 'round', 'TR'], how='left')
        output_df = per_tr_calculation(df)
        save_file(subnum, output_df, 'sub-MONSTERA{}_rolling3_{}.csv'.format(subnum, roi))
        
        summary_df = summarize(output_df)
        summary_df['sub'] = subnum
        summary_df['roi'] = roi
        save_file(subnum, summary_df, 'sub-MONSTERA{}_rolling3_{}_summary.csv'.format(subnum, roi))