<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

![baseeegheader](https://user-images.githubusercontent.com/26397102/117209976-b958e600-adbc-11eb-8f23-d6015a28935e.png)

# PEPPER-Pipeline: A Python-based, Easy, Pre-Processing EEG Reproducible Pipeline
A BIDS compliant, scalable (i.e., HPC-ready), python-based pipeline for processing EEG data in a computationally reproducible framework (leveraging containerized computing using Docker or Singularity). 

The PEPPER-Pipeline tools build off of MNE-python and the sciPy stack. Some tools are convenient wrappers for existing code, whereas others implement novel data processing steps. Note the purpose of the PEPPER-Pipeline is not to reinvent/reimplement the algorithems already implemented by MNE-python. Instead, the "added value" of the PEPPER-Pipeline is in providing a user-friendly pipeline for EEG preprocessing, which is geared towards developmental EEG researchers and is compatible with BIDS, containerization (Docker and Singularity are both supported), and HPC usage. Three methods for working with the pipeline are provided: 1) A singularity image for running on HPCs, a docker image for running on local, and a Conda environment for the dev toolkit.

To facilitate community development and distributed contributions to the PEPPER-Pipeline, development leverages automatic linting of all code (enforcing the PEP8 standard). Moreover, a growing test suite is available for performing unit tests for all features, and the pipeline is structured in a modular way to allow independent modification of speicifc Pipeline steps/features without needing to modify the main run.py script or other functions.

The PEPPER-Pipeline project is a fully-open, community-driven project. We welcome contributions by any/all researchers and data/computer scientists, at all levels. We strive to make all decisions "out in the open" and track all contributions rigorously via git, to faciliate proper recognition and authorship. We hold a weekly meeting that all are welcome to attend, and recordings of prior meetings are all availble for others to view. Please join us in moving this project forward, creating a fully-open, scalable, and reproducible EEG pipeline that all can use.

## Outline

* [Usage](#Usage)
  * [Load-Data](#Load-Data)
  * [Preprocess](#Preprocess)
* [Output](#Output)
  * [Annotations](#Annotations)
  * [Raw-Derivatives](#Raw-Derivatives)
  * [Log-Files](#Log-Files)
* [Pipeline-Steps](#Pipeline-Steps)
  * [Filter](#Filter)
  * [Reject-Bad-Channels](#Reject-Bad-Channels)
  * [ICA](#ICA)
  * [Segment](#Segment)
  * [Final-Reject-Epochs](#Final-Reject-Epochs)
  * [Interpolate](#Interpolate)
  * [Rereference](#Rereference)

Development guidelines and details are listed in [CONTRIBUTING.md](contributing.md)

## Usage

This project comes with a default `user_params.json` file which directly controls data selection, the order of pipeline steps, and their respective parameters. 

To select data and edit parameters, directly edit the fields of this file. 

```json
{

    "load_data": {
        "root": "path-to-data-root",
        "subjects": ["sub1", "sub2"],
        "tasks": ["task1"],
        "exceptions": {
            "subjects": ["sub1"],
            "tasks": ["task1"], 
            "runs": ["run1"]
        },
        "channel-type": "type"
    },
    "preprocess": {
        "filter_data": {
            "param1": "VALUE"
        },
        "bad_channels": {
            "param1": "VALUE"
        },
        "ica": {
            "param1": "VALUE"
        },
        "bad_channels": {
        },
        "ica": {
        },
        "segment_data": {
            "param1": "VALUE",
            "param2": "VALUE"
        },
        "final_reject_epoch": {
            "param1": "VALUE"
        }, 
        "interpolate_data": {
            "param1": "VALUE"
        },
        "rereference_data": {
            "param1": "VALUE"
        }
    },
    "postprocess": {
    }
}
```

### Load-Data
Use this section to select a subset of data by selecting desired subjects, tasks, and any exceptions that you would like to omit. Meta-data `root` and `channel-type` are additionally required. 

For any field where you like to select **all** available data, specify `["*"]` in the respective field. For example, the following selects all available subjects and all available tasks:

```json
"load_data": {
    "root": "path-to-data-root",
    "subjects": ["*"],
    "tasks": ["*"],
    "exceptions": {
        "subjects": "",
        "tasks": "", 
        "runs": ""
    },
    "channel-type": "type"
}
```

The exceptions field works by taking the [cartesian product](https://en.wikipedia.org/wiki/Cartesian_product) of all exception fields. For example, if you would like to omit the datafiles associated with subject-01, task-A, run-01 and run-02, you would specify the following fields:

```json
"load_data": {
    "root": "path-to-data-root",
    "subjects": ["*"],
    "tasks": ["*"],
    "exceptions": {
        "subjects": ["01"],
        "tasks": ["A"], 
        "runs": ["01", "02"]
    },
    "channel-type": "type"
}
```
### Preprocess
Use this section to specify preprocessing pipeline steps and their respective parameters. The default parameter file describes the [pipeline steps](#Pipeline-Steps) described below. 

Directly edit the parameter fields to customize preprocessing attributes. 

## Output 

### Annotations

These output files will contain all research-relevant outputs of the pipeline (e.g. # bad channels rejected, # ICA artifacts rejected, etc.). This file will be built iteratively as the pipeline progresses.

Each file name generated on a subject will follow the BIDS naming standard: `output_preproc_XXX_task_YYY_run_ZZZ.json`

Format:
```javascript
{
    "globalBad_Chans": [1, 23, 119],
    "icArtifacts": [1, 3, 9]
}
```

### Raw-Derivatives
For every pipeline step that executes, an intermediate dataset is written to the specified path. 


## Pipeline-Steps

### 1) Filter

- High pass filter the data using mne function
- Read in the the "highPass" "lowpass" fields from the "user_params.json" file to define filter parameters

### 2) Reject-Bad-Channels

- Auto-detect and remove bad channels (those that are “noisy” for a majority of the recording)
- Write to output file to indicate which channels were detected as bad (write to field "globalBad_chans")

### 3) ICA

Overview: ICA requires a decent amount of [stationarity](https://towardsdatascience.com/stationarity-in-time-series-analysis-90c94f27322#:~:text=In%20t%20he%20most%20intuitive,not%20itself%20change%20over%20time.) in the data. This is often violated by raw EEG. 
    
One way around this is to first make a copy of the eeg data. For the copy, use automated methods to detect noisy portions of data and remove these sections of data. Run ICA on the copied data after cleaning. Finally, take the ICA weights produced by the copied dataset and copy them back to the recording prior to making a copy (and prior to removing sections of noisy data). In this way, we do not have to “throw out” sections of noisy data, while at the same time, we are able to derive an improved ICA decomposition.

1. Prepica
    - Make a copy of the eeg recording
    - For the copied data: high-pass filter at 1 hz
    - For the copied data: segment/epoch (“cut”) the continuous EEG recording into arbitrary 1-second epochs
    - For the copied data: Use automated methods (voltage outlier detection and spectral outlier detection) to detect epochs -that are excessively “noisy” for any channel
    - For the copied data: reject (remove) the noisy periods of data
    - Write to the output file which segments were rejected and based on what metrics
2. Ica
    - For the copied data: run ica
    - Copy the ica weights from the copied data back to the data pre-copy
3. Rejica
    - Using automated methods (TBD) identify ica components that reflect artifacts
    - Remove the data corresponding to the ica-identified-artifacts
    - Write to the output file which ica components were identified as artifacts in the "icArtifacts" field

### 4) Segment
- Segment/epoch (cut) the continuous data into epochs of data, such that the zero point for each epoch is a given marker of interest
- Write to output file which markers were used for epoching purposes, how many of each epoch were created, and how many ms appear before/after the markers of interest

### 5) Final-Reject-Epochs
- Loop through each channel. For a given channel, loop over all epochs for that channel and identify epochs for which that channel, for a given epoch, exceeds either the voltage threshold or spectral threshold. If it exceeds the threshold, reject the channel data for this channel/epoch.
- Write to the output file which channel/epoch intersections were rejected

### 6) Interpolate
- Interpolate missing channels, at the channel/epoch level using a spherical spline interpolation, as implemented in mne
- Interpolate missing channels, at the global level, using a spherical spline interpolation, as implemented in mne
- Write to output file which channels were interpolated and using what method

### 7) Rereference
- Re-reference the data to the average of all electrodes (“average reference”) using the mne function
- Write to output file that data were re-referenced to average


## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/Jonhas"><img src="https://avatars.githubusercontent.com/u/45021859?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Jonhas</b></sub></a><br /><a href="https://github.com/NDCLab/pepper-pipeline/commits?author=Jonhas" title="Code">💻</a> <a href="https://github.com/NDCLab/pepper-pipeline/commits?author=Jonhas" title="Tests">⚠️</a> <a href="#ideas-Jonhas" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/NDCLab/pepper-pipeline/pulls?q=is%3Apr+reviewed-by%3AJonhas" title="Reviewed Pull Requests">👀</a></td>
    <td align="center"><a href="https://github.com/DMRoberts"><img src="https://avatars.githubusercontent.com/u/833695?v=4?s=100" width="100px;" alt=""/><br /><sub><b>DMRoberts</b></sub></a><br /><a href="https://github.com/NDCLab/pepper-pipeline/commits?author=DMRoberts" title="Documentation">📖</a> <a href="https://github.com/NDCLab/pepper-pipeline/commits?author=DMRoberts" title="Code">💻</a> <a href="#ideas-DMRoberts" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-DMRoberts" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/NDCLab/pepper-pipeline/pulls?q=is%3Apr+reviewed-by%3ADMRoberts" title="Reviewed Pull Requests">👀</a> <a href="#projectManagement-DMRoberts" title="Project Management">📆</a></td>
    <td align="center"><a href="https://github.com/georgebuzzell"><img src="https://avatars.githubusercontent.com/u/71228105?v=4?s=100" width="100px;" alt=""/><br /><sub><b>George Buzzell</b></sub></a><br /><a href="https://github.com/NDCLab/pepper-pipeline/commits?author=georgebuzzell" title="Documentation">📖</a> <a href="https://github.com/NDCLab/pepper-pipeline/commits?author=georgebuzzell" title="Code">💻</a> <a href="#ideas-georgebuzzell" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-georgebuzzell" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/NDCLab/pepper-pipeline/pulls?q=is%3Apr+reviewed-by%3Ageorgebuzzell" title="Reviewed Pull Requests">👀</a> <a href="#projectManagement-georgebuzzell" title="Project Management">📆</a> <a href="#mentoring-georgebuzzell" title="Mentoring">🧑‍🏫</a></td>
    <td align="center"><a href="https://github.com/yanbin-niu"><img src="https://avatars.githubusercontent.com/u/79607547?v=4?s=100" width="100px;" alt=""/><br /><sub><b>yanbin-niu</b></sub></a><br /><a href="https://github.com/NDCLab/pepper-pipeline/commits?author=yanbin-niu" title="Code">💻</a> <a href="#ideas-yanbin-niu" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/NDCLab/pepper-pipeline/pulls?q=is%3Apr+reviewed-by%3Ayanbin-niu" title="Reviewed Pull Requests">👀</a></td>
    <td align="center"><a href="https://github.com/SDOsmany"><img src="https://avatars.githubusercontent.com/u/58539319?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Osmany</b></sub></a><br /><a href="https://github.com/NDCLab/pepper-pipeline/commits?author=SDOsmany" title="Code">💻</a> <a href="https://github.com/NDCLab/pepper-pipeline/commits?author=SDOsmany" title="Tests">⚠️</a> <a href="#ideas-SDOsmany" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/NDCLab/pepper-pipeline/pulls?q=is%3Apr+reviewed-by%3ASDOsmany" title="Reviewed Pull Requests">👀</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!