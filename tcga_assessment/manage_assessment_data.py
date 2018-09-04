from __future__ import division
import json
import os
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-b", "--benchmark_data", help="dir where the manifest and the data for the benchmark are stored", required=True)
parser.add_argument("-c", "--cancer_types", nargs='+', help="list of types of cancer selected by the user, separated by spaces", required=True)
parser.add_argument("-p", "--participant_name", help="name of the tool used for prediction", required=True)

args = parser.parse_args()

def main(args):

    # input parameters
    data_dir = args.benchmark_data
    cancer_types = args.cancer_types
    participant = args.participant_name

    generate_manifest(data_dir, cancer_types, participant)
    add_new_tool_to_benchmark(data_dir, cancer_types, participant)
    

def generate_manifest(data_dir, cancer_types, participant):

    info = []

    for cancer in cancer_types:
        if cancer == "UCEC":
            participants = ['MutSig2CV.json', '2020plus.json', 'OncodriveFM.json', 'ActiveDriver.json', 'e-Driver.json', 'OncodriveCLUST.json', 'MuSiC.json']
        else :
            participants = ['MutSig2CV.json', 'compositeDriver.json', '2020plus.json', 'OncodriveFM.json', 'ActiveDriver.json', 'e-Driver.json', 'OncodriveCLUST.json', 'MuSiC.json']

        participants.append(participant + ".json")

        object = {
                    "id" : cancer,
                    "participants": participants
                  }

        info.append(object)

    with open(data_dir + "Manifest.json", 'w') as f:
        json.dump(info, f, sort_keys=True, indent=4, separators=(',', ': '))

def add_new_tool_to_benchmark(data_dir, cancer_types, participant):

    for cancer in cancer_types:

        assessment_file = data_dir + cancer + "_" + participant + "_assessment.json"
        new_location = data_dir + cancer + "/" + participant + ".json"

        os.rename(assessment_file,new_location)

if __name__ == '__main__':

    main(args)