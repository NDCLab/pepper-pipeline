#!/bin/bash
#SBATCH --qos medium
#SBATCH --account iacc_gbuzzell
#SBATCH --partition 6g-per-core
#SBATCH --ntasks=2                 # set tasks equal to subject count
#SBATCH --time=00:02:00            # quit if job hangs after two hours
#SBATCH --job-name=pipeline_run

# load singularity module
module load singularity-3.5.3

# get collection of all available subjects
ls /home/data/NDClab/data/base-eeg/CMI/rawdata/ -F | grep / > subjects.txt

# turn subjects into array
arr=()
while IFS= read -r line; do
  arr+=("$line")
done < subjects.txt

parallel_script=""
for sub in "${arr[@]}"
do
   sub=${sub:4}
   sub_num=${sub::-1}

   parallel_script+="srun --ntasks=1 "
   parallel_script+="singularity exec --bind /home/data/NDClab/data/base-eeg/CMI/derivatives,"
   parallel_script+="/home/data/NDClab/data/base-eeg/CMI/rawdata"
   parallel_script+=" container/run-container.simg python3 run.py & "
done

parallel_script+="wait"

# use singularity container for each available subject and run in parallel
echo $parallel_script
eval "$parallel_script"

# delete subjects.txt 
rm -f subjects.txt
