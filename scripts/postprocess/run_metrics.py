import os
import erp

# def get_erp -- need input: 1) data path; 2) event of interest (string)

data_path = "/Users/yanbinniu/Documents/Projects/tf-pca/OSF/tfpca-tutorial/ptb_data/"

fileList = []
for root, dirs, files in os.walk(data_path):
    for file in files:
        if file.endswith('.fif'):
            fileList.append(os.path.join(root, file))

# get trial level erp for all participants
dataList = erp.get_trial_erp(fileList, 'auditory')

# cal Dan's splithalf