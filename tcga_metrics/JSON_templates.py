import datetime
import pytz


class data_model_templates():

    def write_participant_json(self, ID, community, challenges, participant_name, validated):

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


    def write_assessment_datasets(self, ID, community, challenge, participant_name, metric, metric_value, error, visualization_mode):

        data = {
            "_id": ID,
            "community_id": community,
            "challenge_id": challenge,
            "type": "assessment",
            "metrics": {"metric_id": metric,
                        "value": metric_value,
                        "stderr": error,
                        "visualization": visualization_mode
                        },
            "participant_id": participant_name

        }

        return data