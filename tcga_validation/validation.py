from __future__ import division, print_function
import pandas
import os
import sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-i", "--participant_data", help="list of cancer genes prediction", required=True)
parser.add_argument("-r", "--public_ref_dir", help="directory with the list of cancer genes used to validate the predictions", required=True)
args = parser.parse_args()


def main(args):

    # input parameters
    input_participant = args.participant_data
    public_ref_dir = args.public_ref_dir

    validate_input_data(input_participant,  public_ref_dir)



def validate_input_data(input_participant, public_ref_dir):
    # get participant predicted genes
    try:
        participant_data = pandas.read_csv(input_participant, sep='\t',
                                           comment="#", header=0)
    except:
        sys.exit("ERROR: Submitted data file {} is not in a valid format!".format(input_participant))
    
    predicted_genes = list(participant_data.iloc[:, 0].values)

    # get ids of the submited fields
    data_fields = ['gene', 'transcript', 'protein_change', 'score', 'pvalue', 'qvalue', 'info']
    submitted_fields = list(participant_data.columns.values)

    # get reference dataset to validate against
    validated = False
    for public_ref_rel in os.listdir(public_ref_dir):
        public_ref = os.path.join(public_ref_dir,public_ref_rel)
        if os.path.isfile(public_ref):
            try:
                public_ref_data = pandas.read_csv(public_ref, sep='\t',
                                                  comment="#", header=0)
                cancer_genes = list(public_ref_data.iloc[:, 0].values)
                
                ## validate the fields of the submitted data and if the predicted genes are in the mutations file
                if data_fields == submitted_fields and (set(predicted_genes) < set(cancer_genes)) == True:
                    validated = True
                else:
                    print("WARNING: Submitted data does not validate against "+public_ref,file=sys.stderr)
                    validated = False
            except:
                print("PARTIAL ERROR: Unable to properly process "+public_ref,file=sys.stderr)
                import traceback
                traceback.print_exc()
            
    if validated == True:
        sys.exit(0)
    else:
        sys.exit("ERROR: Submitted data does not validate against any reference data!")


if __name__ == '__main__':

    main(args)







