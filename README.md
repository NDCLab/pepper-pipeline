![baseeegheader](https://user-images.githubusercontent.com/26397102/117209976-b958e600-adbc-11eb-8f23-d6015a28935e.png)

# baseEEG
A Python software tool. Simply execute `run.py` to generate clean EEG data. Details below! 

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

### Log-Files

These output log files will define the verbose outputs of mne functions including warnings and errors for each subject. Format will vary based on pipeline output

Each file name generated on a subject will follow the BIDS naming standard: `output_XXX_task_YYY_run_ZZZ.log`

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

