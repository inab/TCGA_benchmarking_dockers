from __future__ import division
import pandas
import sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-i", "--participant_data", help="list of cancer genes prediction", required=True)
parser.add_argument("-r", "--public_ref", help="list of cancer genes used to validate the predictions", required=True)
args = parser.parse_args()


def main(args):

    # input parameters
    input_participant = args.participant_data
    public_ref = args.public_ref

    validate_input_data(input_participant,  public_ref)



def validate_input_data(input_participant, public_ref):
    # get participant predicted genes
    participant_data = pandas.read_csv(input_participant, sep='\t',
                                       comment="#", header=0)
    predicted_genes = list(participant_data.iloc[:, 0].values)

    # get reference dataset to validate against
    public_ref_data = pandas.read_csv(public_ref, sep='\t',
                                      comment="#", header=0)
    cancer_genes = list(public_ref_data.iloc[:, 0].values)

    # get ids of the submited fields
    data_fields = ['gene', 'transcript', 'protein_change', 'score', 'pvalue', 'qvalue', 'info']
    submitted_fields = list(participant_data.columns.values)

    ## validate the fields of the submitted data and if the predicted genes are in the mutations file
    if data_fields == submitted_fields and (set(predicted_genes) < set(cancer_genes)) == True:
        validated = True
    else:
        validated = False

    if validated == True:
        sys.exit(0)
    else:
        sys.exit("ERROR: Submitted data is not in a valid format!")


if __name__ == '__main__':

    main(args)







