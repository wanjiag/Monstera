for i in 53
do

	if [ ! -d "/home/wanjiag/projects/MONSTERA/derivatives/rois/ASHS/sub-MONSTERA"$i"" ] ; then
		mkdir -p "/home/wanjiag/projects/MONSTERA/derivatives/rois/ASHS/sub-MONSTERA"$i""
	fi

	echo "nohup /gpfs/projects/kuhl_lab/shared/ashs/ashs-fastashs_beta/bin/ashs_main.sh -I sub-MONSTERA"$i" -a /projects/kuhl_lab/shared/ashs/atlases/ashs_atlas_upennpmc_20170810 -g /projects/kuhl_lab/wanjiag/MONSTERA/derivatives/fmriprep/sub-MONSTERA"$i"/anat/sub-MONSTERA"$i"_run-5_desc-preproc_T1w.nii.gz -f /projects/kuhl_lab/wanjiag/MONSTERA/sub-MONSTERA"$i"/anat/sub-MONSTERA"$i"_run-06_T2w.nii.gz -w /projects/kuhl_lab/wanjiag/MONSTERA/derivatives/rois/ASHS/sub-MONSTERA"$i"/ > /projects/kuhl_lab/wanjiag/MONSTERA/derivatives/rois/ASHS/sub-MONSTERA"$i"/nohup.out &"


	nohup /gpfs/projects/kuhl_lab/shared/ashs/ashs-fastashs_beta/bin/ashs_main.sh -I sub-MONSTERA"$i" -a /projects/kuhl_lab/shared/ashs/atlases/ashs_atlas_upennpmc_20170810 -g /projects/kuhl_lab/wanjiag/MONSTERA/derivatives/fmriprep/sub-MONSTERA"$i"/anat/sub-MONSTERA"$i"_run-5_desc-preproc_T1w.nii.gz -f /projects/kuhl_lab/wanjiag/MONSTERA/sub-MONSTERA"$i"/anat/sub-MONSTERA"$i"_run-06_T2w.nii.gz -w /projects/kuhl_lab/wanjiag/MONSTERA/derivatives/rois/ASHS/sub-MONSTERA"$i"/ > /projects/kuhl_lab/wanjiag/MONSTERA/derivatives/rois/ASHS/sub-MONSTERA"$i"/ashs.out &

done

