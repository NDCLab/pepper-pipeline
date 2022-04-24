from metrics.reliability import split_half
from measures.erp import get_trial_erp
import scipy.stats
import pandas as pd
from pathlib import Path
import os
import sys

# Get path from command line
data_path = sys.argv[1]

# tasks = mne_bids.get_entity_vals(data_path, 'task')
tasks = ["surroundSuppBlock1", "surroundSuppBlock2"]
conditions = ['4', '8']
electrode = ['E75']

reliability_results = pd.DataFrame(None, columns=['task', 'condition', 'corr_mean',
                                                  'corr_lower', 'corr_upper', 'reliab_mean',
                                                  'reliab_lower', 'reliab_upper'])

sme_results = pd.DataFrame(None, columns=['subject'] + conditions)

for task in tasks:
    fileList = []
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if (file.endswith('.fif') or file.endswith('.set')) and task in file:
                fileList.append(os.path.join(root, file))
    # if filelist is empty, ie no preprocessed data, skip task
    if not fileList:
        continue
    # print filelist for hpc debugging
    print(fileList)

    # compute splithalf reliability
    # get trial level erp for all participants
    try:
        erp_by_condition = get_trial_erp(fileList, 0.1, 0.15,
                                         conditions, electrode)
    except KeyError as msg:
        print(str(msg))
        continue

    sem_tmp = pd.DataFrame(columns=['subject'] + conditions)
    sem_tmp['subject'] = [Path(filename).stem for filename in fileList]

    # call Dan's splithalf
    for c in conditions:
        condition_data = erp_by_condition[c]
        sem_tmp[c] = [scipy.stats.sem(values) for values in condition_data]

        try:
            split = split_half(condition_data, None)
            # store data into dataframe
            reliability_results = reliability_results.append(pd.DataFrame([[task, c, split.correlation.mean,
                                                                            split.correlation.lower, split.correlation.upper,
                                                                            split.reliability.mean, split.reliability.lower,
                                                                            split.reliability.upper]], columns=['task', 'condition',
                                                                                                                'corr_mean', 'corr_lower',
                                                                                                                'corr_upper', 'reliab_mean',
                                                                                                                'reliab_lower', 'reliab_upper']))

        except Exception as e:
            print(str(e))

    # append sme_results data
    sme_results = sme_results.append(sem_tmp)

reliability_results.to_csv(f'metrics_reliability_{file[-3:]}.csv', index=False)
sme_results.to_csv(f'metrics_sme_{file[-3:]}.csv', index=False)
