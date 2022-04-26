from measures.erp import get_trial_erp
from measures.psd import get_trial_psd
from metrics.reliability import split_half
from pathlib import Path
import os
import scipy.stats
import sys
import pandas as pd

# Get path from command line
data_path = sys.argv[1]

# tasks = mne_bids.get_entity_vals(data_path, 'task')
tasks = ["surroundSuppBlock1", "surroundSuppBlock2"]
conditions = ['4', '8']
electrode = ['E75']
bands = {'delta': [1, 3.9], 'theta': [4, 7.9], 'alpha': [8, 12]}

reliability_erp = pd.DataFrame(None, columns=['task', 'condition', 'corr_mean',
                                              'corr_lower', 'corr_upper', 'reliab_mean',
                                              'reliab_lower', 'reliab_upper'])

reliability_psd = pd.DataFrame(None, columns=['task', 'condition', 'corr_mean',
                                              'corr_lower', 'corr_upper', 'reliab_mean',
                                              'reliab_lower', 'reliab_upper'])

sme_results = pd.DataFrame(None, columns=['subject'] + conditions)

measure_psd = pd.DataFrame(None, columns=['subject'] + [f'{key1}_{key2}' for key2 in bands for key1 in conditions])

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

    # initial computing sem
    sem_tmp = pd.DataFrame(columns=['subject'] + conditions)
    sem_tmp['subject'] = [Path(filename).stem for filename in fileList]

    # compute splithalf reliability
    # get trial level erp for all participants
    try:
        erp_by_condition = get_trial_erp(fileList, 0.1, 0.15, conditions, electrode)
    except KeyError as msg:
        print(str(msg))
        continue

    # call Dan's splithalf for erp
    for c in conditions:
        condition_data = erp_by_condition[c]

        # compute sme
        sem_tmp[c] = [scipy.stats.sem(values) for values in condition_data]

        # erp reliability
        try:
            split_erp = split_half(condition_data, None)
            # store data into dataframe
            reliability_erp = reliability_erp.append(pd.DataFrame([[task, c, split_erp.correlation.mean,
                                                                    split_erp.correlation.lower, split_erp.correlation.upper,
                                                                    split_erp.reliability.mean, split_erp.reliability.lower,
                                                                    split_erp.reliability.upper]],
                                                                  columns=['task', 'condition', 'corr_mean',
                                                                           'corr_lower', 'corr_upper', 'reliab_mean',
                                                                           'reliab_lower', 'reliab_upper']))

        except Exception as e:
            print(str(e))

    # get trial level psd for all participants
    try:
        psd_by_condition, psd_summary = get_trial_psd(fileList, conditions, 1, 12, bands, None, None, electrode, 1000)
    except KeyError as msg:
        print(str(msg))
        continue

    # call Dan's splithalf for psd
    for cond in conditions:
        for band in bands:
            try:
                split_psd = split_half(psd_by_condition[f'{cond}_{band}'], None)
                # store data into dataframe
                reliability_psd = reliability_psd.append(pd.DataFrame([[task, f'{cond}_{band}',
                                                                        split_psd.correlation.mean,
                                                                        split_psd.correlation.lower,
                                                                        split_psd.correlation.upper,
                                                                        split_psd.reliability.mean,
                                                                        split_psd.reliability.lower,
                                                                        split_psd.reliability.upper]],
                                                                      columns=['task', 'condition', 'corr_mean', 'corr_lower',
                                                                               'corr_upper', 'reliab_mean', 'reliab_lower',
                                                                               'reliab_upper']))

            except Exception as e:
                print(str(e))

    # append psd data for each participants
    measure_psd = measure_psd.append(psd_summary)

    # append sme_results data
    sme_results = sme_results.append(sem_tmp)

# to csv
reliability_erp.to_csv(f'metrics_reliability_erp_{file[-3:]}.csv', index=False)
sme_results.to_csv(f'metrics_sme_{file[-3:]}.csv', index=False)
reliability_psd.to_csv(f'metrics_reliability_psd_{file[-3:]}.csv', index=False)
measure_psd.to_csv(f'measures_psd_{file[-3:]}.csv', index=False)
