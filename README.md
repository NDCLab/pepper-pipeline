# baseEEG
Lab-wide EEG scripts

If working on development for this project, please use the docker image located at `base_eeg_docker_files/`. Directions on installation and usage located in `base_eeg_docker_files/readme.txt`. 


## Issues

See issues for current/future work. 

Always assign yourself to an issue before beginning work on it!

If someone is already assigned to an issue, but you want to help, post a comment to ask if you can help before assigning yourself. If no response within 24 hours, then you are free to start work on the issue, but post another comment first to let them know what you will be doing.


## Git Workflow 

![ndcworkflow](https://user-images.githubusercontent.com/26397102/114767588-6e076680-9d2d-11eb-87a7-0f1a48d9984f.png)

Folder/branch organization should follow this convention:

`main`
- no test features
- 100% stable and usable by any lab members 
- *no direct commits*

`->dev`
- Up to date development branch with properly tested/reviewed features 
- *no direct commits*

`-->dev-feature-[featureName]`
- Ongoing development and testing of feature to be pull requested into `dev` 
- *no direct commits*

`--->dev-feature-[featureName]-[yourName]`
- *only* branch available for personal development, must be branched off of `-->dev-feature-[featureName]` branch
- Merged into `-->dev-feature-[featureName]` after pull-request (code review)


## Reminders
1. only push directly (without code review) to dev-feature-[featureName]=[yourName]
2. Must initiate pull request (and assign at least one person) for any higher-level branch
3. Mandatory code review by one person for all pull requests 


## Example Files for Development
- Two example files are currently being used for development:
- For feature-io, we are using this file here: https://drive.google.com/file/d/1-e0-AryZRDmgzXyJtm27vWFq48FY_lUj/view?usp=sharing.
- For all preprocessing features, we are using this file here: https://osf.io/cj2dr/ (use data located in: eeg_matchingpennies->sub-05->eeg


## Roadmap
All features (pipeline steps) can and should be worked on independently and in parallel. Any steps for which implementation relied on a prior step first being completed have been merged into one single feature (e.g., feature-ica contains three steps that must be implemented sequentially). Please self-assign to any feature, read the relevant documentation, reach out with questions, and begin implementation. There is no correct order to implement any of these steps.

For now, when working to implement a given step, please use this (BIDS-formatted) test file: https://osf.io/cj2dr/
(use data located in: eeg_matchingpennies->sub-05->eeg. Once feature-io is complete, everyone should switch to using a new test file created using feature-io.

The Preprocessing pipeline assumes that data is already in BIDS format. Thus, any scripts (e.g. feature-filter-io) to convert data to BIDS format are NOT part of the preprocessing pipeline. Thus, all steps of the preprocessing pipeline should be written in such a way as to assume a BIDS folder structure file already exists and that standard BIDS metadata files exist (which can be read in to govern preprocessing). Moreover, all outputs of the preprocessing stream should either be in line with existing BIDS standards or if they relate to a feature that there is not yet a BIDS standard for, the developer should set things up in a way that is in line with general BIDS principles.

Given that the final pipeline will read from a user-supplied json file called "user_params.json" and write to an annotations file called "annotations_preproc.json", all independent feature development should refer to a common standard format for these two files to allow for easier integration of features for the final pipeline.

Format of "user_params.json" (please add additional fields as necessary; do not hesitate to add fields. Basically, when working on a feature, if you think there is a parameter that users might want to control, just add another field to the "user_params.json" file. There is no issue with having lots of fields with default values.)

{
"highPass": [.3],
"lowpass": [50],
]
}

Format of "annotations_preproc.json" (please add additional fields as necessary; do not hesitate to add fields. Basically, when working on a feature, if you think there is a value that is computed that might be of use to users, please add it to the "annotations_preproc.json" file.)

{
"globalBad_Chans": [1, 23, 119],
"icArtifacts": [1, 3, 9],,
}

Steps/features of the pipline:

Feature-filter
-High pass filter the data using mne function
-Read in the the "highPass" "lowpass" fields from the "user_params.json" file to define filter parameters

Feature-badchans
-auto-detect and remove bad channels (those that are “noisy” for a majority of the recording)
-write to annotations file to indicate which channels were detected as bad (write to field "globalBad_chans")

Feature-ica
This feature includes three main (and sequential) steps: 1. Prepica; 2. Ica; 3. Rejica
Overview: ICA requires a decent amount of stationarity in the data. This is often violated by raw EEG. One way around this is to first make a copy of the eeg data. For the copy, use automated methods to detect noisy portions of data and remove these sections of data. Run ICA on the copied data after cleaning. Finally, take the ICA weights produced by the copied dataset and copy them back to the recording prior to making a copy (and prior to removing sections of noisy data). In this way, we do not have to “throw out” sections of noisy data, while at the same time, we are able to derive an improved ICA decomposition.
Prepica
-Make a copy of the eeg recording
-For the copied data: segment/epoch (“cut”) the continuous EEG recording into arbitrary 1-second epochs
-For the copied data: Use automated methods (voltage outlier detection and spectral outlier detection) to detect epochs -that are excessively “noisy” for any channel
-For the copied data: reject (remove) the noisy periods of data
-Write to the annotations file which segments were rejected and based on what metrics
Ica
-For the copied data: run ica
-Copy the ica weights from the copied data back to the data pre-copy
Rejica
-Using automated methods (TBD) identify ica components that reflect artifacts
-Remove the data corresponding to the ica-identified-artifacts
-Write to the annotations file which ica components were identified as artifacts in the "icArtifacts" field

Feature-segment
-segment/epoch (cut) the continuous data into epochs of data, such that the zero point for each epoch is a given marker of interest
-write to annotations file which markers were used for epoching purposes, how many of each epoch were created, and how many ms appear before/after the markers of interest

Feature-finalrej
-loop through each channel. For a given channel, loop over all epochs for that channel and identify epochs for which that channel, for a given epoch, exceeds either the voltage threshold or spectral threshold. If it exceeds the threshold, reject the channel data for this channel/epoch.
-write to the annotations file which channel/epoch intersections were rejected

Feature-interp
-interpolate missing channels, at the channel/epoch level using a spherical spline interpolation, as implemented in mne
-interpolate missing channels, at the global level, using a spherical spline interpolation, as implemented in mne
-write to annotations file which channels were interpolated and using what method

Feature-reref
-re-reference the data to the average of all electrodes (“average reference”) using the mne function
-write to annotations file that data were re-referenced to average

