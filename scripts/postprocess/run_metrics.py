import os
import postprocess

from scripts.reliability.reliability import split_half

data_path = "/home/data/NDClab/datasets/cmi-dataset/derivatives/preprocessed"

fileList = []
for root, dirs, files in os.walk(data_path):
    for file in files:
        if file.endswith('.fif'):
            fileList.append(os.path.join(root, file))

# compute splithalf reliability
# get trial level erp for all participants
datalist1, datalist2 = postprocess.get_trial_erp(fileList, 0, 0.1, '12', '5')

# call Dan's splithalf
print(split_half(datalist1, datalist2))

# compute SME
sme = postprocess.sme(fileList, 0, 0.1, ['12', '5'], ['E1', 'E2'])
