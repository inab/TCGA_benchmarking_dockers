import datetime

"""
    INFO:
    This class contains functions that generate JSON objects with structure compatible with the Elixir 
    Benchmarking Data Model (https://github.com/inab/benchmarking-data-model)
    It should be used in the docker declarations to generate the output files in any benchmarking workflow which might be implemented in the 
    OpenEBench infrastructure.
    Benchmarking workflows architecture can be found in https://github.com/inab/TCGA_benchmarking_workflow
    Docker declarations for each step: https://github.com/inab/TCGA_visualizer

"""

class data_model_templates():

    """
        Participant datasets should be generated in the VALIDATION step
        The minimal required properties for this dataset are:
        - ID - the id assigned to this dataset by the community
        - community - the benchmarking community name/OEB-id
        - challenges - an array with one or more challenges where the participant is evaluated
        - participant_name - name/OEB-id of the tool which generated the dataset
        - validated(boolean) - whether this file passed the validation script or not

    """
    def write_participant_dataset(self, ID, community, challenges, participant_name, validated):

        if validated == True:
            status = "ok"
        else:
            status = "corrupted"

        data = {
            "_id":ID,
            "community_id": community,
            "challenge_ids": challenges,
            "type": "participant",
            "datalink": {
                "attrs": ["archive"],
                "validation_date": str(datetime.datetime.now().replace(microsecond=0).isoformat()),
                "status": status
            },
            "participant_id": participant_name,

        }

        return data

    """
        Assessment datasets should be generated in the METRICS COMPUTATION step
        The minimal required properties for this dataset are:
        - ID - the id assigned to this dataset by the community
        - community - the benchmarking community name/OEB-id
        - challenge - the challenge where the metrics were computed
        - participant_name - name/OEB-id of the tool which is evaluated in this assessment
        - metric - the name of the unique metric which correspond to this assessment
        - metric_value - the numeric value of the metric
        - error - the standard error/deviation for the computed metric (can be 0)

    """
    def write_assessment_dataset(self, ID, community, challenge, participant_name, metric, metric_value, error):

        data = {
            "_id": ID,
            "community_id": community,
            "challenge_id": challenge,
            "type": "assessment",
            "metrics": {"metric_id": metric,
                        "value": metric_value,
                        "stderr": error
                        },
            "participant_id": participant_name

        }

        return data