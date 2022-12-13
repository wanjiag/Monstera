#!/bin/bash

# directories

group_dir = /projects/kuhl_lab
container = "${group_dir}"/shared/containers/fmriprep-21.0.0.simg
usrname = wanjiag
study = MONSTERA
study_dir = "${group_dir}"/"${usrname}"/"${study}"

set subject list
subject_list=`cat subject_list_fmriprep.txt` 

# Loop through subjects and run job_mriqc
for subject in $subject_list; do

subid=`echo $subject|awk '{print $1}' FS=","`
  
sbatch --export=ALL,subid=${subid},group_dir=${group_dir},study_dir=${study_dir},study=${study},container=${container} --job-name fmriprep --partition=long --cpus-per-task=28 --mem=75G --time=30:00:00 -o "${study_dir}"/fmriprep/log/"${subid}"_fmriprep_output.txt -e "${study_dir}"/fmriprep/log/"${subid}"_fmriprep_error.txt job_fmriprep.sh
        
done
