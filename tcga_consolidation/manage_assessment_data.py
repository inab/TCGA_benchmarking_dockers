#!/usr/bin/env python3

from __future__ import division
import requests
import json
import os
import logging
import sys
from argparse import ArgumentParser
from assessment_chart import assessment_chart

DEFAULT_eventMark = '2018-04-05'
DEFAULT_OEB_API = "https://dev-openebench.bsc.es/api/scientific/staged/graphql"
DEFAULT_eventMark_id = "OEBE0010000000"

def main(args):

    # input parameters
    data_dir = args.benchmark_data
    participant_path = args.participant_data
    output_dir = args.output
    offline = args.offline
    
    # Assuring the output directory does exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # read participant metrics
    participant_data = read_participant_data(participant_path)
    if offline is None:
        response = query_OEB_DB(DEFAULT_eventMark_id)
        getOEBAggregations(response, data_dir)
    generate_manifest(data_dir, output_dir, participant_data)

##get existing aggregation datasets for that challenges
def query_OEB_DB(bench_event_id):
    json_query = {'query': """query AggregationQuery($bench_event_id: String) {
    getChallenges(challengeFilters: {benchmarking_event_id: $bench_event_id}) {
        _id
        acronym
        metrics_categories{
          metrics {
            metrics_id
            orig_id
          }
        }
        datasets(datasetFilters: {type: "aggregation"}) {
                _id
                _schema
                orig_id
                community_ids
                challenge_ids
                datalink {
                    inline_data
                }
        }
    }
}""",
                'variables': {
                    'bench_event_id': bench_event_id
                }
            }
    try:
        url = DEFAULT_OEB_API
        # get challenges and input datasets for provided benchmarking event
        r = requests.post(url=url, json=json_query, headers={'Content-Type': 'application/json'})
        response = r.json()
        data = response.get("data")
        if data is None:
            logging.fatal("For {} got response error from graphql query: {}".format(bench_event_id, r.text))
            sys.exit(6)
        if len(data["getChallenges"]) == 0:
            logging.fatal("No challenges associated to benchmarking event " + bench_event_id +
                          " in OEB. Please contact OpenEBench support for information about how to open a new challenge")
            sys.exit()
        else:
            return data.get('getChallenges')
    except Exception as e:

        logging.exception(e)
        
def getOEBAggregations(response, output_dir):
    for challenge in response:
        
        challenge['datasets'][0]['datalink']["inline_data"] = json.loads(challenge['datasets'][0]["datalink"]["inline_data"])
        
        for metrics in challenge['metrics_categories'][0]['metrics']:
            if metrics['metrics_id'] == challenge['datasets'][0]['datalink']["inline_data"]["visualization"]["x_axis"]:
                challenge['datasets'][0]['datalink']["inline_data"]["visualization"]["x_axis"] = metrics['orig_id'].split(":")[-1]
            elif metrics['metrics_id'] == challenge['datasets'][0]['datalink']["inline_data"]["visualization"]["y_axis"]:
                challenge['datasets'][0]['datalink']["inline_data"]["visualization"]["y_axis"] = metrics['orig_id'].split(":")[-1]
        
        #replace tool_id for participant_id (for the visualitzation)
        for i in challenge['datasets'][0]['datalink']['inline_data']['challenge_participants']:
            i["participant_id"] = i.pop("tool_id")
        
        new_aggregation = {
            "_id": challenge['datasets'][0]['_id'],
            "challenge_ids": [
                 challenge['acronym']
            ],
            'datalink': challenge['datasets'][0]['datalink']
        }
        with open(os.path.join(output_dir, challenge['acronym']+".json"), mode='w', encoding="utf-8") as f:
            json.dump(new_aggregation, f, sort_keys=True, indent=4, separators=(',', ': '))
        
        
        
         
    

def read_participant_data(participant_path):
    participant_data = {}

    with open(participant_path, mode='r', encoding="utf-8") as f:
        result = json.load(f)
        for item in result:
            participant_data.setdefault(item['challenge_id'], []).append (item)

    return participant_data

def generate_manifest(data_dir,output_dir, participant_data):

    info = []

    for cancer, metrics_file in participant_data.items():

        cancer_dir = os.path.join(output_dir,cancer)
        if not os.path.exists(cancer_dir):
            os.makedirs(cancer_dir)
        participants = []
        
        
        cancer_oeb_data_dir = os.path.join(data_dir, cancer)
        cancer_oeb_data = cancer_oeb_data_dir + ".json"

        if os.path.isfile(cancer_oeb_data):
            # Transferring the public participants data
            with open(cancer_oeb_data) as f:
                aggregation_file = json.loads(f.read())
           
            # get default id for metrics in x and y axis
            metric_X = aggregation_file["datalink"]["inline_data"]["visualization"]["x_axis"]
            metric_Y = aggregation_file["datalink"]["inline_data"]["visualization"]["y_axis"]
        else:
            challenge_participants = []
            
            # get default id for metrics in x and y axis
            metric_X = None
            metric_Y = None
            for metrics_data in metrics_file:
                if metric_X is None:
                    metric_X = metrics_data["metrics"]["metric_id"]
                elif metric_Y is None:
                    metric_Y = metrics_data["metrics"]["metric_id"]
                else:
                    break
            
            # Setting the defaults in case nothing was found
            if metric_X is None:
                metric_X = "TPR"
            if metric_Y is None:
                metric_Y = "precision"
            
            aggregation_file = {
                "_id": "TCGA:{}_{}_Aggregation".format(DEFAULT_eventMark, cancer),
                "challenge_ids": [
                    cancer
                ],
                "datalink": {
                    "inline_data": {
                        "challenge_participants": challenge_participants,
                        "visualization": {
                            "type": "2D-plot",
                            "x_axis": metric_X,
                            "y_axis": metric_Y
                        }
                    }
                },
                "type": "aggregation"
            }
            
            # Get the info from the files in the directory
            if os.path.isdir(cancer_oeb_data_dir):
                print("Reading {}".format(cancer_oeb_data_dir))
                for entry in os.scandir(cancer_oeb_data_dir):
                    if entry.is_file() and entry.name.endswith(".json"):
                        with open(entry.path, mode="r", encoding="utf-8") as ep:
                            metrics_content = json.load(ep)
                            if metrics_content.get("cancer_type") == cancer:
                                challenge_participants.append({
                                    "metric_x": metrics_content["x"],
                                    "metric_y": metrics_content["y"],
                                    "participant_id": metrics_content["toolname"]
                                })

        # add new participant data to aggregation file
        new_participant_data = {}
        participant_id = '(unknown)'
        for metrics_data in metrics_file:
            participant_id = metrics_data["participant_id"]
            if metrics_data["metrics"]["metric_id"] == metric_X:
                new_participant_data["metric_x"] = metrics_data["metrics"]["value"]
            elif metrics_data["metrics"]["metric_id"] == metric_Y:
                new_participant_data["metric_y"] = metrics_data["metrics"]["value"]
        # copy the assessment files to output directory
        rel_new_location = participant_id + ".json"
        new_location = os.path.join(cancer_dir, rel_new_location)
        with open(new_location, mode='w', encoding="utf-8") as f:
            json.dump(metrics_file, f, sort_keys=True, indent=4, separators=(',', ': '))

        new_participant_data["participant_id"] = participant_id
        aggregation_file["datalink"]["inline_data"]["challenge_participants"].append(new_participant_data)

        # add the rest of participants to manifest
        for name in aggregation_file["datalink"]["inline_data"]["challenge_participants"]:
            participants.append(name["participant_id"])

        #copy the updated aggregation file to output directory
        summary_dir = os.path.join(cancer_dir,cancer + ".json")
        with open(summary_dir, 'w') as f:
            json.dump(aggregation_file, f, sort_keys=True, indent=4, separators=(',', ': '))
            

        # Let's draw the assessment charts!
        assessment_chart.print_chart(cancer_dir, summary_dir, cancer, "RAW")
        assessment_chart.print_chart(cancer_dir, summary_dir, cancer, "SQR")
        assessment_chart.print_chart(cancer_dir, summary_dir, cancer, "DIAG")

        #generate manifest
        obj = {
            "id" : cancer,
            "participants": participants
        }

        info.append(obj)

    with open(os.path.join(output_dir, "Manifest.json"), mode='w', encoding="utf-8") as f:
        json.dump(info, f, sort_keys=True, indent=4, separators=(',', ': '))
if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-p", "--participant_data", help="path where the data for the participant is stored", required=True)
    parser.add_argument("-b", "--benchmark_data", help="dir where the data for the benchmark will be or is stored", required=True)
    parser.add_argument("-o", "--output", help="output directory where the manifest and output JSON files will be written", required=True)
    parser.add_argument("--offline", help="offline mode; existing benchmarking datasets will be read from the benchmark_data", required=False, type= bool)
    args = parser.parse_args()

    main(args)
