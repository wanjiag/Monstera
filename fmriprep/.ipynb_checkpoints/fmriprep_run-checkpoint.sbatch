#!/bin/bash
#SBATCH --partition=short        ### Partition (like a queue in PBS)
#SBATCH --job-name=fMRIprep      ### Job Name
#SBATCH --output=/projects/kuhl_lab/wanjiag/NEUDIF/scripts/fmriprep/log/NEUDIF.%j.out        ### File in which to store job output
#SBATCH --error=/projects/kuhl_lab/wanjiag/NEUDIF/scripts/fmriprep/log/NEUDIF.%j.err          ### File in which to store job error messages
#SBATCH --time=0-23:00:00       ### Wall clock time limit in Days-HH:MM:SS
#SBATCH --nodes=1               ### Number of nodes needed for the job
#SBATCH --ntasks-per-node=16     ### Number of tasks to be launched per Node
#SBATCH --mem=40000	### --mem is memory per node

module load singularity

singularity run -e --bind /projects/kuhl_lab/wanjiag:/projects/kuhl_lab/wanjiag /projects/kuhl_lab/shared/containers/fmriprep-1.5.0.simg /projects/kuhl_lab/wanjiag/NEUDIF/bids_data /projects/kuhl_lab/wanjiag/NEUDIF/bids_data/derivatives participant --participant-label 32 --output-space {template,T1w,fsaverage5,fsnative} --mem_mb 36000 --nthreads 16 --fs-license-file /projects/kuhl_lab/wanjiag/NEUDIF/scripts/license.txt -w /projects/kuhl_lab/wanjiag/NEUDIF/bids_data/derivatives/fmriprep_tmp/

###singularity run --bind ${abs}:${bind_path} ${image} ${bids} ${output} participant --participant-label 01 --output-space {template,T1w,fsaverage5,fsnative} --mem_mb 20000 --nthreads 16 --fs-license-file ${fs_license} -w ${wk}
