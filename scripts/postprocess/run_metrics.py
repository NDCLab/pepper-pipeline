import mne_bids
import postprocess
from reliability import split_half

import csv
import os
import sys

# Get path from command line
data_path = sys.argv[1]

tasks = mne_bids.get_entity_vals(data_path, 'task')

# gen csv file name using task
file_name = "metrics.csv"

# hard code split_half column names
columns = ["task", "corr_mean", "corr_lower", "corr_upper", "reliab_mean",
           "reliab_lower", "reliab_upper", "sme"]

# Create task dict for data storage
task_data = {}

for task in tasks:
    fileList = []
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file.endswith('.fif') and task in file:
                fileList.append(os.path.join(root, file))
    # if filelist is empty, ie no preprocessed data, skip task
    if not fileList:
        continue
    # init dict for metric storage
    metric_data = {key: None for key in columns}

    # compute splithalf reliability
    # get trial level erp for all participants
    datalist1, datalist2 = postprocess.get_trial_erp(fileList, 0.1, 0.15, '4')

    # call Dan's splithalf
    try:
        split = split_half(datalist1, datalist2)
        # store data into dict
        metric_data["corr_mean"] = split.correlation.mean
        metric_data["corr_lower"] = split.correlation.lower
        metric_data["corr_upper"] = split.correlation.upper

        metric_data["reliab_mean"] = split.reliability.mean
        metric_data["reliab_lower"] = split.reliability.lower
        metric_data["reliab_upper"] = split.reliability.upper
    except Exception as e:
        for key in metric_data:
            if key != "task":
                metric_data[key] = str(e)
                print(metric_data)
    metric_data["task"] = task

    # calc sme
    try:
        sme = postprocess.sme(fileList, 0.1, 0.15, ['4'], ['E75'])
        unpacked = str([str(val[0]) for val in sme])
        metric_data["sme"] = unpacked
    except Exception as e:
        metric_data["sme"] = str(e)

    task_data[task] = metric_data

with open(file_name, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(columns)

    for key in task_data:
        metrics = list(task_data[key].values())
        writer.writerow(metrics)
