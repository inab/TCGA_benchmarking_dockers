from __future__ import division
import io
import shutil
import json
import os
import fnmatch
from argparse import ArgumentParser

def main(args):

    # input parameters
    data_dir = args.benchmark_data
    participant_dir = args.participant_data
    output_dir = args.output
    
    # Assuring the output directory does exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cancer_types_part = get_cancer_types(participant_dir)
    generate_manifest(data_dir, output_dir, cancer_types_part)
    
"""
	Gets the cancer types from the participant result files
"""
def get_cancer_types(participant_dir):
    cancer_types = {}
    
    for result_file in os.listdir(participant_dir):
        abs_result_file = os.path.join(participant_dir, result_file)
        if fnmatch.fnmatch(result_file,"*.json") and os.path.isfile(abs_result_file):
            with io.open(abs_result_file,mode='r',encoding="utf-8") as f:
                result = json.load(f)
                cancer_types.setdefault(result['cancer_type'],[]).append((result['toolname'],abs_result_file))
    
    return cancer_types

def generate_manifest(data_dir,output_dir, cancer_types):

    info = []

    for cancer,cancer_participants in cancer_types.items():
        cancer_dir = os.path.join(output_dir,cancer)
        
        participants = []
        
        cancer_data_dir = os.path.join(data_dir,cancer)
        if os.path.isdir(cancer_data_dir):
            # Transferring the public participants data
            shutil.copytree(cancer_data_dir,cancer_dir)
            
            # Gathering the public participants
            for public_participant in os.listdir(cancer_dir):
		part_fullpath = os.path.join(cancer_dir,public_participant)
                if fnmatch.fnmatch(public_participant,"*.json") and os.path.isfile(part_fullpath):
                    participants.append(public_participant)
            
        # And now, the participants
        # copytree should have created the directory ... if it run
        if not os.path.exists(cancer_dir):
            os.makedirs(cancer_dir)
        for (participant,abs_result_file) in cancer_participants:
            rel_new_location = participant + ".json"
            new_location = os.path.join(cancer_dir, rel_new_location)
            shutil.copy(abs_result_file,new_location)
            participants.append(rel_new_location)
        
        obj = {
            "id" : cancer,
            "participants": participants
        }
        
        info.append(obj)
    
    with io.open(os.path.join(output_dir, "Manifest.json"), mode='w', encoding="utf-8") as f:
        jdata = json.dumps(info, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.write(unicode(jdata,"utf-8"))

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-p", "--participant_data", help="dir where the data for the participant is stored", required=True)
    parser.add_argument("-b", "--benchmark_data", help="dir where the data for the benchmark are stored", required=True)
    parser.add_argument("-o", "--output", help="output directory where the manifest and output JSON files will be written", required=True)

    args = parser.parse_args()

    main(args)
