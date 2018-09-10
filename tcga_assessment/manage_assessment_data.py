from __future__ import division
import io
import shutil
import json
import os
import fnmatch
from argparse import ArgumentParser

import matplotlib.pyplot as plt

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

def pareto_frontier(Xs, Ys, maxX=True, maxY=True):
    # Sort the list in either ascending or descending order of X
    myList = sorted([[Xs[i], Ys[i]] for i, val in enumerate(Xs, 0)], reverse=maxX)
    # Start the Pareto frontier with the first value in the sorted list
    p_front = [myList[0]]
    # Loop through the sorted list
    for pair in myList[1:]:
        if maxY:
            if pair[1] >= p_front[-1][1]:  # Look for higher values of Y
                p_front.append(pair)  # and add them to the Pareto frontier
        else:
            if pair[1] <= p_front[-1][1]:  # look for lower values of Y
                p_front.append(pair)  # and add them to the pareto frontier
    # Turn resulting pairs back into a list of Xs and Ys
    p_frontX = [pair[0] for pair in p_front]
    p_frontY = [pair[1] for pair in p_front]
    return p_frontX, p_frontY


def print_chart(data_dir, participants_datasets, cancer_type):
    tools = []
    x_values = []
    y_values = []
    for tool, metrics in participants_datasets.iteritems():
        tools.append(tool)
        x_values.append(metrics[0])
        y_values.append(metrics[1])

    ax = plt.subplot()
    for i, val in enumerate(tools, 0):
        markers = [".", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+",
                   "x", "X",
                   "D",
                   "d", "|", "_", ","]
        colors = ['#5b2a49', '#a91310', '#9693b0', '#e7afd7', '#fb7f6a', '#0566e5', '#00bdc8', '#cf4119', '#8b123f',
                  '#b35ccc', '#dbf6a6', '#c0b596', '#516e85', '#1343c3', '#7b88be']

        ax.errorbar(x_values[i], y_values[i], linestyle='None', marker=markers[i],
                    markersize='15', markerfacecolor=colors[i], markeredgecolor=colors[i], capsize=6,
                    ecolor=colors[i], label=tools[i])

    # change plot style
    # set plot title

    plt.title("Cancer Driver Genes prediction benchmarking - " + cancer_type, fontsize=18, fontweight='bold')

    # set plot title depending on the analysed tool

    ax.set_xlabel("True Positive Rate - % driver genes correctly predicted", fontsize=12)
    ax.set_ylabel("Precision - % true positives over total predicted", fontsize=12)

    # Shrink current axis's height  on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.25,
                     box.width, box.height * 0.75])

    # Put a legend below current axis
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), markerscale=0.7,
               fancybox=True, shadow=True, ncol=5, prop={'size': 12})


    # set the axis limits
    x_lims = ax.get_xlim()
    plt.xlim(x_lims)
    y_lims = ax.get_ylim()
    plt.ylim(y_lims)
    if x_lims[0] >= 1000:
        ax.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    if y_lims[0] >= 1000:
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda y, loc: "{:,}".format(int(y))))

    # set parameters for optimization
    better = "top-right"
    max_x = True
    max_y = True

    # get pareto frontier and plot
    p_frontX, p_frontY = pareto_frontier(x_values, y_values, maxX=max_x, maxY=max_y)
    plt.plot(p_frontX, p_frontY, linestyle='--', color='grey', linewidth=1)
    # append edges to pareto frontier
    if better == 'bottom-right':
        left_edge = [[x_lims[0], p_frontX[-1]], [p_frontY[-1], p_frontY[-1]]]
        right_edge = [[p_frontX[0], p_frontX[0]], [p_frontY[0], y_lims[1]]]
        plt.plot(left_edge[0], left_edge[1], right_edge[0], right_edge[1], linestyle='--', color='red',
                 linewidth=1)
    elif better == 'top-right':
        left_edge = [[x_lims[0], p_frontX[-1]], [p_frontY[-1], p_frontY[-1]]]
        right_edge = [[p_frontX[0], p_frontX[0]], [p_frontY[0], y_lims[0]]]
        plt.plot(left_edge[0], left_edge[1], right_edge[0], right_edge[1], linestyle='--', color='red',
                 linewidth=1)

    # add 'better' annotation and quartile numbers to plot
    if better == 'bottom-right':
        plt.annotate('better', xy=(0.98, 0.04), xycoords='axes fraction',
                     xytext=(-30, 30), textcoords='offset points',
                     ha="right", va="bottom",
                     arrowprops=dict(facecolor='black', shrink=0.05, width=0.9))

    elif better == 'top-right':
        plt.annotate('better', xy=(0.98, 0.95), xycoords='axes fraction',
                     xytext=(-30, -30), textcoords='offset points',
                     ha="right", va="top",
                     arrowprops=dict(facecolor='black', shrink=0.05, width=0.9))



    # plt.show()
    outname = data_dir + cancer_type + "/" + cancer_type + "_benchmark.svg"
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    fig.savefig(outname, dpi=100)

    plt.close("all")

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-p", "--participant_data", help="dir where the data for the participant is stored", required=True)
    parser.add_argument("-b", "--benchmark_data", help="dir where the data for the benchmark are stored", required=True)
    parser.add_argument("-o", "--output", help="output directory where the manifest and output JSON files will be written", required=True)

    args = parser.parse_args()

    main(args)
