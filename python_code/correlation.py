import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from glob import glob 
from os.path import join as opj
import os
import re

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
    
    df['round'] = df['round'].astype('int')
    df['trial'] = df['trial'].astype('int')
    
    if subnum == 47:
        df = df.loc[df['within_trial_TR']!=25]
        
        problem_trial = df.loc[(df['round']==1)&(df['trial']==1)]
        added_sec = pd.DataFrame([[47,1,1,50,'pair2_north','pole','False','similar', 'na']], columns = problem_trial.columns)
        problem_trial = pd.concat([problem_trial, added_sec])
        problem_trial['within_trial_TR'] = problem_trial.groupby(['sub','round','trial'])['TR'].rank(method = 'dense').astype('int')
        problem_trial = problem_trial.sort_values(by=['within_trial_TR'])
        
        print(df.shape)
        df = df.loc[(df['round']!=1)|(df['trial']!=1)]
        print(df.shape)
        df = pd.concat([df, problem_trial])

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

preprocess_dir = '/projects/kuhl_lab/wanjiag/MONSTERA/derivatives/preprocess'
fMRI_dir = "/home/wanjiag/projects/MONSTERA/derivatives/csv_files/fMRI/"
output_dir = "/home/wanjiag/projects/MONSTERA/derivatives/csv_files/python/"
behav_dir = "/home/wanjiag/projects/MONSTERA/derivatives/csv_files/behavior/"

f_list = [x for x in glob(os.path.join(preprocess_dir, '*sub-MONSTERA*/'))]
subs = list(map(lambda f: f[len(os.path.commonpath(f_list))+1:-1], f_list))
subs.sort()
print(subs)

bad = ['sub-MONSTERA01', 'sub-MONSTERA02', 'sub-MONSTERA03', 'sub-MONSTERA04', 'sub-MONSTERA05',
        'sub-MONSTERA13', 'sub-MONSTERA14', 'sub-MONSTERA20', 'sub-MONSTERA23', 'sub-MONSTERA24', 
       'sub-MONSTERA27', 'sub-MONSTERA30', 'sub-MONSTERA34']

todo_subs = list(set(subs) - set(bad))
todo_subs.sort()
print(todo_subs)

for sub in todo_subs:
    subnum = re.findall('\d+', sub)[0]
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
        # df = behav_df.merge(fmri_df, on=['sub', 'round', 'TR'], how='left')
        # output_df = per_tr_calculation(df)
        # save_file(subnum, output_df, 'sub-MONSTERA{}_norolling_{}.csv'.format(subnum, roi))
        
        #calculating rolling data
        rolling_df = fmri_df.groupby(['sub','round']).rolling(3, center = True, method = 'table').mean()
        rolling_df = rolling_df.drop(columns= ['sub','round']).reset_index().drop(columns= 'level_2')
        df = behav_df.merge(rolling_df, on=['sub', 'round', 'TR'], how='left')
        output_df = per_tr_calculation(df)
        save_file(subnum, output_df, 'sub-MONSTERA{}_rolling3_{}.csv'.format(subnum, roi))