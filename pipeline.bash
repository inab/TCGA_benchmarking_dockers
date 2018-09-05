#!/bin/bash

#Run the tcga visualizer pipeline

REALPATH="$(realpath "$0")"
BASEDIR="$(dirname "$REALPATH")"
case "$BASEDIR" in
	/*)
		true
		;;
	*)
		BASEDIR="${PWD}/$BASEDIR"
		;;
esac

TCGA_DIR="${BASEDIR}"/TCGA_visualizer_data

if [ $# -gt 1 ] ; then 
	input="$1"
	RESDIR="$2"
	shift 2
	
	if [ $# -gt 0 ] ; then
		PARTICIPANT="$1"
		shift
	else
		PARTICIPANT=NEW_PARTICIPANT
	fi
	
	if [ $# -gt 0 ] ; then
		CANCER_TYPES="$@"
	else
		CANCER_TYPES="ACC BRCA"
	fi
	
	cat <<EOF
* Running parameters

  Input: $input
  Results: $RESDIR
  Participant: $PARTICIPANT
  Cancer types: $CANCER_TYPES
EOF
	
	if [ ! -f "$input" ] ; then
		echo "ERROR: input file does not exist" 1>&2
		exit 1
	fi
	echo "* Deriving input directory"
	inputRealPath="$(realpath "$input")"
	inputBasename="$(basename "$input")"
	INPUTDIR="$(dirname "$inputRealPath")"
	case "$INPUTDIR" in
		/*)
			true
			;;
		*)
			INPUTDIR="${PWD}/$INPUTDIR"
			;;
	esac
	
	echo "* Creating $RESDIR (if it does not exist)"
	mkdir -p "$RESDIR"
	
	ASSESSDIR="${TCGA_DIR}"/data
	METRICS_DIR="${TCGA_DIR}"/metrics_ref_datasets
	PUBLIC_REF_DIR="${TCGA_DIR}"/public_ref

	docker run --rm -u $UID -v "${INPUTDIR}":/app/input -v "${REFDIR}":/app/ref tcga_validation \
		python validation.py -i /app/input/"${inputBasename}" -r /app/ref/ && \
	docker run --rm -u $UID -v "${INPUTDIR}":/app/input -v "${METRICS_DIR}":/app/metrics -v "${RESDIR}":/app/results tcga_metrics \
		python compute_metrics.py -i /app/input/ACC.txt -c $CANCER_TYPES -m /app/metrics/ -p "${PARTICIPANT}" -o /app/results/ && \
	docker run --rm -u $UID -v "${ASSESSDIR}":/app/assess -v "${RESDIR}":/app/results tcga_assessment \
		python manage_assessment_data.py -b /app/assess/ /app/results/ -o /app/results/ -c $CANCER_TYPES -p "${PARTICIPANT}"


	#Build de imagenes:

	#docker build -t tcga_validation .
	#docker build -t tcga_metrics .
	#docker build -t manage_assessment_data .
else
	echo "Usage: $0 input_file results_dir [participant_id [cancer_type]*]\n"
fi
