import os
import postprocess
from reliability import split_half
import sys
import csv

data_path = "/home/data/NDClab/datasets/cmi-dataset/derivatives/PEPPER_pipeline/PEPPER_pipeline_preprocessed"
original_stdout = sys.stdout
fileList = []
for root, dirs, files in os.walk(data_path):
    for file in files:
        if file.endswith('.fif') and "surroundSuppBlock" in file:
            fileList.append(os.path.join(root, file))

# compute splithalf reliability
# get trial level erp for all participants
datalist1, _ = postprocess.get_trial_erp(fileList, 0.15, 0.2, '4')

# call Dan's splithalf
split = split_half(datalist1, None)
with open('split_half_50.txt', 'w') as f:
    sys.stdout = f
    f.write("Split half measure\n")
    print(split)
    sys.stdout = original_stdout
    

# compute SME
sme = postprocess.sme(fileList, 0.15, 0.2, ['4'], ['E75'])
with open('sme_50.csv', 'w') as f:
    # unpack sme
    unpacked = [ str(val[0]) for val in sme ]
    print(unpacked)
    write = csv.writer(f)
    write.writerow(unpacked)
