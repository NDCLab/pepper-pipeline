import mne_bids
import pandas
from metrics.sme import sme
from metrics.reliability import split_half
from measures.erp import get_trial_erp

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
    try:
        datalist1, _ = get_trial_erp(fileList, 0.1, 0.15, '4')
    except KeyError:
        continue

    # call Dan's splithalf
    try:
        split = split_half(datalist1, None)
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

    task_data[task] = metric_data

with open(file_name, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(columns)

    for key in task_data:
        metrics = list(task_data[key].values())
        writer.writerow(metrics)

# cal sme
sme_result = sme(fileList, 0.1, 0.15, ['4'], ['E75'])
sme_result.to_csv('output/sme.csv', index = False)
