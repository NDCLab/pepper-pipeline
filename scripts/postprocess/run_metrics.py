import os
import erp

data_path = "/Users/yanbinniu/Documents/Projects/tf-pca/OSF/tfpca-tutorial/ptb_data/"

fileList = []
for root, dirs, files in os.walk(data_path):
    for file in files:
        if file.endswith('.fif'):
            fileList.append(os.path.join(root, file))

# get trial level erp for all participants
datalist1, datalist2 = erp.get_trial_erp(fileList, 0, 0.1, 'auditory', 'visual')

# cal Dan's splithalf
