import pydicom
import sys
from os.path import join as opj
from os import rename
from pathlib import Path
from re import sub
from glob import glob
import simplejson as json

if '/projects/lcni/jolinda/shared/site-packages' not in sys.path:
    sys.path.append('/projects/lcni/jolinda/shared/site-packages')

import dicom2bids

dcmdir = '/projects/lcni/dcm/kuhl_lab/Kuhl/MONSTERA/*'

bd = dicom2bids.bids_dict()

# Add field maps
bd.add('se_epi_ap', datatype = 'fmap', suffix = 'epi', dir = 'ap') 
bd.add('se_epi_pa', datatype = 'fmap', suffix = 'epi', dir = 'pa') 

# Add structural scans
bd.add('mprage_p2', 
       datatype = 'anat', 
       suffix = 'T1w')
#old T2 name
#bd.add('t2_tse_cor65slice', 
#       datatype = 'anat', 
#       suffix = 'T2w')
bd.add('t2_tse_cor_65slice_2ave', 
       datatype = 'anat', 
       suffix = 'T2w')

# Add EPI sequences
bd.add('EPI_01', 
       datatype = 'func',
       task = '01',
       suffix = 'bold')
bd.add('EPI_02', 
       datatype = 'func', 
       task = '02',
       suffix = 'bold')
bd.add('EPI_03', 
       datatype = 'func', 
       task = '03',
       suffix = 'bold')
bd.add('EPI_04', 
       datatype = 'func', 
       task = '04',
       suffix = 'bold')
bd.add('EPI_05', 
       datatype = 'func', 
       task = '05',
       suffix = 'bold')
bd.add('EPI_06', 
       datatype = 'func', 
       task = '06',
       suffix = 'bold')
bd.add('EPI_07', 
       datatype = 'func', 
       task = '07',
       suffix = 'bold')
bd.add('EPI_08', 
       datatype = 'func', 
       task = '08',
       suffix = 'bold')
bd.add('EPI_09', 
       datatype = 'func', 
       task = '09',
       suffix = 'bold')
bd.add('EPI_10', 
       datatype = 'func', 
       task = '10',
       suffix = 'bold')

# Adding single band reference
bd.add('EPI_01_SBRef', 
       datatype = 'func',
       task = '01',
       suffix = 'sbref')
bd.add('EPI_02_SBRef', 
       datatype = 'func', 
       task = '02',
       suffix = 'sbref')
bd.add('EPI_03_SBRef', 
       datatype = 'func', 
       task = '03',
       suffix = 'sbref')
bd.add('EPI_04_SBRef', 
       datatype = 'func', 
       task = '04',
       suffix = 'sbref')
bd.add('EPI_05_SBRef', 
       datatype = 'func', 
       task = '05',
       suffix = 'sbref')
bd.add('EPI_06_SBRef', 
       datatype = 'func', 
       task = '06',
       suffix = 'sbref')
bd.add('EPI_07_SBRef', 
       datatype = 'func', 
       task = '07',
       suffix = 'sbref')
bd.add('EPI_08_SBRef', 
       datatype = 'func', 
       task = '08',
       suffix = 'sbref')
bd.add('EPI_09_SBRef', 
       datatype = 'func', 
       task = '09',
       suffix = 'sbref')
bd.add('EPI_10_SBRef', 
       datatype = 'func', 
       task = '10',
       suffix = 'sbref')

bidsdir = '/projects/kuhl_lab/wanjiag/MONSTERA/'
files = glob(opj(bidsdir, 'sub-MONSTERA*'))
processed_ids = [x.split('/')[5].split('-')[1] for x in files]
processing_sub_list = []

for dir in glob(dcmdir):
    subid = dir.split('/')[7].split('_')[0]
    if subid not in processed_ids:
        
        processing_sub_list.append(subid)
        print(subid)
        
        if subid == 'MONSTERA18':
            dir = '/home/wanjiag/projects/MONSTERA/derivatives/special_subs_dcm/MONSTERA18_20220909_101935'
        if subid == 'MONSTERA26':
            dir = '/home/wanjiag/projects/MONSTERA/derivatives/special_subs_dcm/MONSTERA26_20221021_142348'
        dicom2bids.Convert(dir, bidsdir, bids_dict=bd, account = 'kuhl_lab')

for id in processing_sub_list:
    func_files = glob(opj(bidsdir, 'sub-'+id, 'func','*'))
    for cur_f in func_files:
        rename(cur_f, sub(r"run\-\d+_", "", cur_f))
        print(cur_f)
        print(sub(r"run\-\d+_", "", cur_f))
        print()


# Edit fmap metadata
def write_metadata(json_file, intended_list):
    """Write IntendedFor field to json metadata.

    Parameters
    ----------
    json_file : os.PathLike
        Metadata json file.
    intended_list : list[str]
        Intended file list.

    """
    # Add field
    json_file.chmod(0o644)
    with json_file.open("r") as f:
        data = json.load(f)
    with json_file.open("w") as f:
        data["IntendedFor"] = intended_list
        json.dump(data, f, indent=2)
    json_file.chmod(0o444)

bids_dir = Path(bidsdir)

for sub_id in processing_sub_list:
    print(f"Processing sub-{sub_id}...")
    # BOLD files list which fmap intended for
    f_lst = list(
        sorted(bids_dir.joinpath(f"sub-{sub_id}", "func").glob("*_bold.nii.gz"))
    )
    intended_list = [f"func/{f.name}" for f in f_lst]
    # Add intended for field to json
    if bids_dir.joinpath(f"sub-{sub_id}", "fmap").exists():
        json_file_list = list(
            sorted(bids_dir.joinpath(f"sub-{sub_id}", "fmap").glob("*.json"))
        )
        for json_file in json_file_list:
            write_metadata(json_file, intended_list)
    print(f"Completed sub-{sub_id} ...")
