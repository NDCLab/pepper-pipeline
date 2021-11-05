import os
import postprocess

data_path = "/Users/yanbinniu/Documents/Projects/tf-pca/OSF/tfpca-tutorial/ptb_data/"

fileList = []
for root, dirs, files in os.walk(data_path):
    for file in files:
        if file.endswith('.fif'):
            fileList.append(os.path.join(root, file))

# compute splithalf reliability
# get trial level erp for all participants
datalist1, datalist2 = postprocess.get_trial_erp(fileList, 0, 0.1, 'auditory', 'visual')
# call Dan's splithalf

# compute SME
sme = postprocess.sme(fileList, 0, 0.1, ['auditory', 'visual'], ['E1', 'E2'])
