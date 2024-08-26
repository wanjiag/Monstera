#!/bin/bash
#SBATCH --partition=short        ### Partition (like a queue in PBS)
#SBATCH --job-name=roi      ### Job Name
#SBATCH --output=./logs/03_roi_%j.out         ### File in which to store job output
#SBATCH --error=./logs/03_roi_%j.err          ### File in which to store job error messages
#SBATCH --time=0-23:00:00       ### Wall clock time limit in Days-HH:MM:SS
#SBATCH --nodes=1               ### Number of nodes needed for the job
#SBATCH --ntasks-per-node=1     ### Number of tasks to be launched per Node
#SBATCH --account=kuhl_lab      ### Account used for job submission
#SBATCH --partition=kuhl
#SBATCH --mail-user=wanjiag@uoregon.edu
#SBATCH --mail-type=END 


for i in 53
do

	if [ ! -d "/home/wanjiag/projects/MONSTERA/derivatives/rois/ASHS/sub-MONSTERA"$i"" ] ; then
		mkdir -p "/home/wanjiag/projects/MONSTERA/derivatives/rois/ASHS/sub-MONSTERA"$i""
	fi

	echo "nohup /gpfs/projects/kuhl_lab/shared/ashs/ashs-fastashs_beta/bin/ashs_main.sh -I sub-MONSTERA"$i" -a /projects/kuhl_lab/shared/ashs/atlases/ashs_atlas_upennpmc_20170810 -g /projects/kuhl_lab/wanjiag/MONSTERA/derivatives/fmriprep/sub-MONSTERA"$i"/anat/sub-MONSTERA"$i"_run-5_desc-preproc_T1w.nii.gz -f /projects/kuhl_lab/wanjiag/MONSTERA/sub-MONSTERA"$i"/anat/sub-MONSTERA"$i"_run-06_T2w.nii.gz -w /projects/kuhl_lab/wanjiag/MONSTERA/derivatives/rois/ASHS/sub-MONSTERA"$i"/ > /projects/kuhl_lab/wanjiag/MONSTERA/derivatives/rois/ASHS/sub-MONSTERA"$i"/nohup.out &"


	nohup /gpfs/projects/kuhl_lab/shared/ashs/ashs-fastashs_beta/bin/ashs_main.sh -I sub-MONSTERA"$i" -a /projects/kuhl_lab/shared/ashs/atlases/ashs_atlas_upennpmc_20170810 -g /projects/kuhl_lab/wanjiag/MONSTERA/derivatives/fmriprep/sub-MONSTERA"$i"/anat/sub-MONSTERA"$i"_run-5_desc-preproc_T1w.nii.gz -f /projects/kuhl_lab/wanjiag/MONSTERA/sub-MONSTERA"$i"/anat/sub-MONSTERA"$i"_run-06_T2w.nii.gz -w /projects/kuhl_lab/wanjiag/MONSTERA/derivatives/rois/ASHS/sub-MONSTERA"$i"/ > /projects/kuhl_lab/wanjiag/MONSTERA/derivatives/rois/ASHS/sub-MONSTERA"$i"/ashs.out &

done

