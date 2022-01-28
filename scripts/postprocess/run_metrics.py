import mne_bids
from metrics.sme import sme
from metrics.reliability import split_half
from measures.erp import get_trial_erp
import scipy.stats
import pandas as pd
from pathlib import Path
import csv
import os
import sys

# Get path from command line
data_path = sys.argv[1]

# tasks = mne_bids.get_entity_vals(data_path, 'task')
tasks = ["surroundSuppBlock1", "surroundSuppBlock2", "surroundSuppBlock3"]
conditions = ['4', '8']
electrode = ['E75']

# gen csv file name using task
file_name = "metrics.csv"

# hard code split_half column names
columns = ["task", "condition", "corr_mean", "corr_lower", "corr_upper", "reliab_mean",
           "reliab_lower", "reliab_upper"]

# metrics file header (could replace with pandas DataFrame)
with open(file_name, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(columns)

task_data = {}
total_fileList = []

for task in tasks:
    fileList = []
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if (file.endswith('.set') or file.endswith('.fif')) and task in file:
                fileList.append(os.path.join(root, file))
    # if filelist is empty, ie no preprocessed data, skip task
    if not fileList:
        continue
    # print filelist for hpc debugging
    print(fileList)
    # append to total fileList for sme computation
    total_fileList += fileList
    # init dict for metric storage
    metric_data = {key: None for key in columns}

    # compute splithalf reliability
    # get trial level erp for all participants
    try:
        erp_by_condition = get_trial_erp(fileList, 0.1, 0.15, conditions, electrode)
    except KeyError:
        continue

    sem_output = pd.DataFrame(columns=['subject'] + conditions)
    sem_output['subject'] = [Path(filename).stem for filename in fileList]

    # call Dan's splithalf
    for c in conditions:
        condition_data = erp_by_condition[c]
        sem_output[c] = [scipy.stats.sem(values) for values in condition_data]

        try:
            split = split_half(condition_data, None)
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
        metric_data["condition"] = c

        task_data[task] = metric_data

        # append data
        with open(file_name, 'a', newline='') as f:
            writer = csv.writer(f)
            for key in task_data:
                metrics = list(task_data[key].values())
                writer.writerow(metrics)

sem_output.to_csv(f'sme_new_{task}.csv', index=False)

# cal sme
sme_result = sme(total_fileList, 0.1, 0.15, conditions, electrode)
sme_result.to_csv('sme.csv', index=False)
