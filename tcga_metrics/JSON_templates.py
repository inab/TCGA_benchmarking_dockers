import datetime


class data_model_templates():

    def write_participant_json(self, community, challenges, participant_name, file_path, input_dataset):

        data = {
            "datalink": {
                "uri": file_path,
                "attrs": ["archive"],
                "validation_date": str(datetime.datetime.now().replace(microsecond=0).isoformat()),
                "status": "ok"
            },
            "type": "participant",
            "_schema": "https://www.elixir-europe.org/excelerate/WP2/json-schemas/1.0/Dataset",
            "community_ids": community,
            "challenge_ids": challenges,
            "depends_on": {
                "tool_id": participant_name,
                "rel_dataset_ids": [
                    {
                        "dataset_id": input_dataset,
                    }
                ]
            }
        }

        return data


    def write_assessment_datasets(self, community, challenge, participant_name, metric, metric_value, participant_data_id, ref_data_id):

        data = {

            "type": "assessment",
            "datalink": {
                "inline_data": {"value": metric_value}
            },
            "depends_on": {
                "tool_id": participant_name,
                "metrics_id": community + ":" + metric,
                "rel_dataset_ids": [
                    {
                        "dataset_id": participant_data_id
                    },
                    {
                        "dataset_id": ref_data_id
                    }
                ]
            },
            "_schema": "https://www.elixir-europe.org/excelerate/WP2/json-schemas/1.0/Dataset",
            "community_ids": community,
            "challenge_ids": [challenge]
        }

        return data