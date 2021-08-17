<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-7-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

![baseeegheader](https://user-images.githubusercontent.com/26397102/117209976-b958e600-adbc-11eb-8f23-d6015a28935e.png)

# PEPPER-Pipeline: A Python-based, Easy, Pre-Processing EEG Reproducible Pipeline
A BIDS compliant, scalable (i.e., HPC-ready), python-based pipeline for processing EEG data in a computationally reproducible framework (leveraging containerized computing using Docker or Singularity). 

The PEPPER-Pipeline tools build off of MNE-python and the sciPy stack. Some tools are convenient wrappers for existing code, whereas others implement novel data processing steps. Note the purpose of the PEPPER-Pipeline is not to reinvent/reimplement the algorithems already implemented by MNE-python. Instead, the "added value" of the PEPPER-Pipeline is in providing a user-friendly pipeline for EEG preprocessing, which is geared towards developmental EEG researchers and is compatible with BIDS, containerization (Docker and Singularity are both supported), and HPC usage. Three methods for working with the pipeline are provided: 1) A singularity image for running on HPCs, a docker image for running on local, and a Conda environment for the dev toolkit.

To facilitate community development and distributed contributions to the PEPPER-Pipeline, development leverages automatic linting of all code (enforcing the PEP8 standard). Moreover, a growing test suite is available for performing unit tests for all features, and the pipeline is structured in a modular way to allow independent modification of speicifc Pipeline steps/features without needing to modify the main run.py script or other functions.

The PEPPER-Pipeline project is a fully-open, community-driven project. We welcome contributions by any/all researchers and data/computer scientists, at all levels. We strive to make all decisions "out in the open" and track all contributions rigorously via git, to faciliate proper recognition and authorship. We hold a weekly meeting that all are welcome to attend, and recordings of prior meetings are all availble for others to view. Please join us in moving this project forward, creating a fully-open, scalable, and reproducible EEG pipeline that all can use.

## Outline

* [Usage](#usage)
  * [Load Data](#load-data)
  * [Preprocess](#preprocess)
* [Output](#output)
  * [Annotations](#annotations)
  * [Raw Derivatives](#raw-derivatives)
* [Pipeline Steps](#pipeline-steps)
  * [1-Filter](#1-filter)
  * [2-Reject Bad Channels](#2-reject-bad-channels)
  * [3-ICA](#3-ica)
  * [4-Segment](#4-segment)
  * [5-Final Reject Epochs](#5-final-reject-epochs)
  * [6-Interpolate](#6-interpolate)
  * [7-Re-reference](#7-re-reference)
* [Contributors](#Contributors)

Development guidelines and details are listed in [CONTRIBUTING.md](CONTRIBUTING.md)

### Usage

This project comes with a default `user_params.json` file that controls data selection, the order of pipeline steps, and their respective parameters.

To select data and edit parameters, directly edit the fields of `user_params.json`.


```json
{
  "load_data": {
    "root": "CMI/rawdata",
    "subjects": ["*"],
    "tasks": ["*"],
    "exceptions": {
      "subjects": "",
      "tasks": "", 
      "runs": ""
    },
    "channel-type": "eeg"
  }, 

  "preprocess": {
    "filter_data": {
      "l_freq": 0.3, 
      "h_freq": 40
    },
    "identify_badchans_raw": {
    },
    "ica_raw": {
      "montage": "GSN-HydroCel-129"
    },
    "segment_data": {
      "tmin": -0.2, 
      "tmax": 0.5, 
      "baseline": null, 
      "picks": null, 
      "reject_tmin": null, 
      "reject_tmax": null, 
      "decim": 1, 
      "verbose": false, 
      "preload": true
    },
    "final_reject_epoch": {
    }, 
    "interpolate_data": {
      "mode": "accurate", 
      "method": null,
      "reset_bads": true
    },
    "reref_raw": {
    }
  },
  "output_data": {
    "root": "CMI"
  }
}
```

**Load Data**
This section directly controls the selection of data to be preprocessed. Note, all data **must** be in BIDS format before any preprocessing can be done!

In this section, you input the path to your data (`root`) and the channel-type (`channel-type`).

You may optionally use this section to select a subset of data by specifying desired subjects, tasks, and any exceptions to omit from the output.

For any field where you would like to select **all** available data, specify `["*"]` in the respective field.

The exceptions field works by taking the [cartesian product](https://en.wikipedia.org/wiki/Cartesian_product) of all exception fields. 

**EXAMPLES**

The following examples show how to select data using the `load_data` section, from the least granular to most. 

1. Select all data 

```json
    "load_data": {
        "root": "~/PATH_TO_DATA/",
        "subjects": ["*"],
        "tasks": ["*"],
        "exceptions": {
            "subjects": "",
            "tasks": "", 
            "runs": ""
        },
        "channel-type": "eeg"
    },
```

2. Select data w/a singular exception

```json
    "load_data": {
        "root": "~/PATH_TO_DATA/",
        "subjects": ["*"],
        "tasks": ["*"],
        "exceptions": {
            "subjects": ["*"],
            "tasks": ["*"], 
            "runs": ["2"]
        },
        "channel-type": "eeg"
    },
```
*In this example, every single data file that contains "run-2" will be omitted from the preprocessing process*

3. Select a subset of data w/multiple exceptions 

```json
    "load_data": {
        "root": "~/PATH_TO_DATA/",
        "subjects": ["NDARAB793GL3"],
        "tasks": ["*"],
        "exceptions": {
            "subjects": "NDARAB793GL3",
            "tasks": "Video1", 
            "runs": ["*"]
        },
        "channel-type": "eeg"
    },
```
*In this example, only the "NDARAB793GL3" subject is selected to be processed. Every single data file that strictly contains "sub-NDARAB793GL3" and "Video1" will be omitted from the preprocessing process*

**Preprocess**

Use this section to customize pre-processing pipeline steps and their respective parameters. The `user_params.json` file includes default values for each of the [pipeline steps](#pipeline-steps) described below.

### Output 

#### Annotations
One output file per subject is created, containing all research-relevant outputs of the pre-processing (e.g., the number of bad channels rejected, the number of ICA artifacts rejected, etc.). This file is built iteratively as the pipeline progresses.

Each file generated follows BIDS naming conventions for file naming: `output_preproc_XXX_task_YYY_run_ZZZ.json`

Here is an example of file contents:
```javascript
{
    "globalBad_Chans": [1, 23, 119],
    "icArtifacts": [1, 3, 9]
}
```

#### Raw Derivatives
For every pipeline step that executes, an intermediate dataset is written to the specified output path under the intermediate folder 'PEPPER_intermediate'. 

The final preprocessed datafile is written to a final 'PEPPER_preprocessed'. 

### Pipeline Steps

#### 1-Filter

- High-pass filter the data using MNE functions
- Read in the "high pass" "low pass" fields from the `user_params.json` file to define filter parameters

#### 2-Reject Bad Channels

- Auto-detect and remove bad channels (those that are “noisy” for a majority of the recording)
- Write to output file (field "globalBad_chans") to indicate which channels were detected as bad

#### 3-Independent Component Analysis

  Overview: ICA requires a decent amount of [stationarity](https://towardsdatascience.com/stationarity-in-time-series-analysis-90c94f27322#:~:text=In%20t%20he%20most%20intuitive,not%20itself%20change%20over%20time.) in the data. This is often violated by raw EEG. One way around this is to first make a copy of the EEG data using automated methods to detect noisy portions of data and removing these sections. ICA is then run on the copied data after cleaning. The ICA weights produced by the copied dataset are copied back into original recording. In this way, we do not have to “throw out” sections of noisy data, while, at the same time, we are able to derive an improved ICA decomposition.

1. Prepica
    - Make a copy of the EED recording
    - For the copied data: high-pass filter at 1 Hz
    - For the copied data: segment by epoch  to “cut” the continuous EEG recording into arbitrary 1-second epochs
    - For the copied data: use automated methods (voltage outlier detection and spectral outlier detection) to detect epochs that are excessively “noisy” for any channel
    - For the copied data: reject (remove) the noisy periods of data
    - Write to the output file which segments were rejected and based on what metrics
2. ICA
    - Run ICA on the copied data
    - Copy the ICA weights from the copied data back to the pre-copy data
3. Rejica
    - Use automated methods (TBD) to identify ICA components that reflect artifacts
    - Remove the data corresponding to the identified artifacts
    - Write to the output file (field "icArtifacts") which ICA components were identified as artifacts

#### 4-Segment
- Segment by epoch to "cut" the continuous data into epochs of data such that the zero point for each epoch is a given marker of interest
- Write to output file (field "XXX") which markers were used for epoching purposes, how many of each epoch were created, and how many milliseconds were retained before/after the markers of interest

#### 5-Final Reject Epochs
- Loop through each channel. For a given channel, loop over all epochs for that channel and identify epochs for which that channel, for a given epoch, exceeds either the voltage threshold or spectral threshold. If it exceeds the threshold, reject the channel data for this channel/epoch.
- Write to the output file ("field XXX") which channel/epoch intersections were rejected

#### 6-Interpolate
- Interpolate missing channels, at the channel/epoch level, using a spherical spline interpolation, as implemented in MNE
- Interpolate missing channels, at the global level, using a spherical spline interpolation, as implemented in MNE
- Write to output file (field "XXX") which channels were interpolated and using what method

#### 7-Re-reference
- Re-reference the data to the average of all electrodes (“average reference”) using the MNE function
- Write to output file (field "XXX") which data were re-referenced to average

## Work in Development
This `main` branch contains completed releases for this project. For all work-in-progress, please switch over to the `dev` branches.

## Contributing
If you are interested in contributing, please read our [CONTRIBUTING.md](CONTRIBUTING.md) file.


### Contributors 

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/georgebuzzell"><img src="https://avatars.githubusercontent.com/u/71228105?v=4?s=100" width="100px;" alt=""/><br /><sub><b>George Buzzell</b></sub></a><br /><a href="https://github.com/NDCLab/pepper-pipeline/commits?author=georgebuzzell" title="Documentation">📖</a> <a href="https://github.com/NDCLab/pepper-pipeline/commits?author=georgebuzzell" title="Code">💻</a> <a href="#ideas-georgebuzzell" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-georgebuzzell" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/NDCLab/pepper-pipeline/pulls?q=is%3Apr+reviewed-by%3Ageorgebuzzell" title="Reviewed Pull Requests">👀</a> <a href="#projectManagement-georgebuzzell" title="Project Management">📆</a> <a href="#mentoring-georgebuzzell" title="Mentoring">🧑‍🏫</a></td>
    <td align="center"><a href="https://github.com/DMRoberts"><img src="https://avatars.githubusercontent.com/u/833695?v=4?s=100" width="100px;" alt=""/><br /><sub><b>DMRoberts</b></sub></a><br /><a href="https://github.com/NDCLab/pepper-pipeline/commits?author=DMRoberts" title="Documentation">📖</a> <a href="https://github.com/NDCLab/pepper-pipeline/commits?author=DMRoberts" title="Code">💻</a> <a href="#ideas-DMRoberts" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-DMRoberts" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/NDCLab/pepper-pipeline/pulls?q=is%3Apr+reviewed-by%3ADMRoberts" title="Reviewed Pull Requests">👀</a> <a href="#projectManagement-DMRoberts" title="Project Management">📆</a></td>
    <td align="center"><a href="https://www.kaggle.com/fsaidmur"><img src="https://avatars.githubusercontent.com/u/26397102?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Farukh Saidmuratov</b></sub></a><br /><a href="https://github.com/NDCLab/pepper-pipeline/commits?author=F-said" title="Code">💻</a> <a href="https://github.com/NDCLab/pepper-pipeline/issues?q=author%3AF-said" title="Bug reports">🐛</a> <a href="https://github.com/NDCLab/pepper-pipeline/commits?author=F-said" title="Documentation">📖</a> <a href="#infra-F-said" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#ideas-F-said" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/NDCLab/pepper-pipeline/pulls?q=is%3Apr+reviewed-by%3AF-said" title="Reviewed Pull Requests">👀</a></td>
    <td align="center"><a href="https://github.com/yanbin-niu"><img src="https://avatars.githubusercontent.com/u/79607547?v=4?s=100" width="100px;" alt=""/><br /><sub><b>yanbin-niu</b></sub></a><br /><a href="#data-yanbin-niu" title="Data">🔣</a><a href="https://github.com/NDCLab/pepper-pipeline/commits?author=yanbin-niu" title="Code">💻</a> <a href="#ideas-yanbin-niu" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/NDCLab/pepper-pipeline/pulls?q=is%3Apr+reviewed-by%3Ayanbin-niu" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/NDCLab/pepper-pipeline/issues?q=author%3AF-said" title="Bug reports">🐛</a></td>
    <td align="center"><a href="http://stevenwtolbert.com"><img src="https://avatars.githubusercontent.com/u/40587948?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Steven William Tolbert</b></sub></a><br /><a href="https://github.com/NDCLab/pepper-pipeline/commits?author=stevenwtolbert" title="Code">💻</a> <a href="#infra-stevenwtolbert" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#ideas-stevenwtolbert" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/NDCLab/pepper-pipeline/pulls?q=is%3Apr+reviewed-by%3Astevenwtolbert" title="Reviewed Pull Requests">👀</a></td>
    <td align="center"><a href="https://github.com/SDOsmany"><img src="https://avatars.githubusercontent.com/u/58539319?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Osmany</b></sub></a><br /><a href="https://github.com/NDCLab/pepper-pipeline/commits?author=SDOsmany" title="Code">💻</a> <a href="https://github.com/NDCLab/pepper-pipeline/commits?author=SDOsmany" title="Tests">⚠️</a> <a href="#ideas-SDOsmany" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/NDCLab/pepper-pipeline/pulls?q=is%3Apr+reviewed-by%3ASDOsmany" title="Reviewed Pull Requests">👀</a></td>
    <td align="center"><a href="https://github.com/Jonhas"><img src="https://avatars.githubusercontent.com/u/45021859?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Jonhas</b></sub></a><br /><a href="https://github.com/NDCLab/pepper-pipeline/commits?author=Jonhas" title="Code">💻</a> <a href="https://github.com/NDCLab/pepper-pipeline/commits?author=Jonhas" title="Tests">⚠️</a> <a href="#ideas-Jonhas" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/NDCLab/pepper-pipeline/pulls?q=is%3Apr+reviewed-by%3AJonhas" title="Reviewed Pull Requests">👀</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!