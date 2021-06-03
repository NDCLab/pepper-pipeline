from scripts.data import load
from scripts.data import write

import scripts.preprocess.preprocess as preproc
from collections import ChainMap

user_params = load.load_param("user_params.json")

# get preprocessing steps
preprocess_steps = user_params["preprocess"]
# get collection of subjects from user_params
root, subjects, ch_type = load.init_data(user_params)

# TODO: Should analysis be run on select tasks, runs, sessions for subjects?
for subj in subjects:
    subject_files = load.load_subject_files(root, subj, ch_type)
    # get only eeg data files
    subject_files = [s for s in subject_files if s.suffix == ch_type]

    for file in subject_files:

        ses, task, run = file.session, file.task, file.run
        eeg_obj = load.load_raw(root, subj, ses, task, run, ch_type)

        outputs = [None] * len(preprocess_steps)
        # for each pipeline step in user_params, execute with parameters
        for idx, (func, params) in enumerate(preprocess_steps.items()):
            eeg_obj, outputs[idx] = getattr(preproc, func)(eeg_obj, **params)
            write.write_eeg_data(eeg_obj, func, subj, ses, task, ch_type, root)

        # TODO: write output_preproc to appropriate path
        # collect outputs of each step and annotate changes
        output = dict(ChainMap(*outputs))
        write.read_dict_to_json(output)
