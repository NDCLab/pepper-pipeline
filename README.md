![baseeegheader](https://user-images.githubusercontent.com/26397102/117209976-b958e600-adbc-11eb-8f23-d6015a28935e.png)

# baseEEG
A set of python-based tools for EEG processing designed for developmental EEG researchers. These tools build off MNE-Python and the SciPy stack. Some are convenient wrappers for existing code while others implement novel data processing steps. These tools are not intended to reinvent/re-implement extant MNE-Python algorithms, but rather to provide a set of user-friendly pipelines for EEG pre- and post-processing that are specifically geared towards developmental EEG researchers.

## Roadmap
Currently, the development of baseEEG is focused on optimizing an automated, flexible, and easy-to-use pipeline dedicated to EEG (as opposed to MEG) pre-processing. Additionally, there is an unofficial script template for converting EEG data to BIDS format (heavily leveraging MNE-BIDS). Following the optimization of import and pre-processing tools, development will focus on building out a common core of EEG processing tools to handle ERP, time-frequency, and source-based analyses. 

Current readme and contributing files focus on the baseEEG pre-processing pipeline.

## Outline

* [Usage](#usage)
  * [Load Data](#load-data)
  * [Preprocess](#preprocess)
* [Output](#output)
  * [Annotations](#annotations)
  * [Raw Derivatives](#raw-derivatives)
  * [Log Files](#log-files)
* [Pipeline-Steps](#pipeline-steps)
  * [Filter](#filter)
  * [Reject Bad Channels](#reject-bad-channels)
  * [ICA](#ica)
  * [Segment](#segment)
  * [Final Reject Epochs](#final-reject-epochs)
  * [Interpolate](#interpolate)
  * [Re-reference](#re-reference)

Development guidelines and details are listed in [CONTRIBUTING.md](contributing.md)

__________________FROM JESS
It seems to me that "Outline" above should possibly be renamed "Usage" (as the vast majority of this file is usage instructions, right?  In which case, this "Usage" section should possibly be renamed "Selecting Parameters"?
__________________FROM JESS

### Usage

This project comes with a default `user_params.json` file that controls data selection, the order of pipeline steps, and their respective parameters.

To select data and edit parameters, directly edit the fields of `user_params.json`.

__________________FROM JESS
To be honest, the sections that follow are more clear and take up less real estate, so I think you could just delete this whole code block below without sacrificing any clarity.
__________________FROM JESS

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

#### Load Data
In this section, you must input the path to your data (`root`) and the type of channel (`channel-type`).

You may optionally use this section to select a subset of data by specifying desired subjects, tasks, and any exceptions to omit from the output.

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
__________________FROM JESS
The above is really nice and clear.  Suggestion: make it totally specific by inputting a faux root and appropriate channel-type.
__________________FROM JESS

The exceptions field works by taking the [cartesian product](https://en.wikipedia.org/wiki/Cartesian_product) of all exception fields. For example, if you would like to omit the datafiles associated with subject-01, task-A, run-01 and run-02, you would specify the following fields:

__________________FROM JESS
Sorry, I'm not strong in set theory.  Would this omit datafiles associated with runs 01 and 02 for task A of subject 01?  Or all datafiles for runs 01 and 02 (all subjects, all tasks)?  Also suggest using the faux root and channel type used above, if you like my earlier suggestion.
__________________FROM JESS

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

#### Preprocess

__________________FROM JESS
I pasted in the code block from above, but I'm not sure how to mark that this isn't the start of the code (which is, of course, available just a few lines up)?  Also, three general questions about this portion of the code block:
1. Why does "bad_channels" exist twice?
2. Why does "ica" exist twice?
3. Where does a user specify the output filepath?
__________________FROM JESS

```json
//
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
```

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
For every pipeline step that executes, an intermediate dataset is written to the specified path. 

#### Log Files
These output log files contain the verbose outputs of MNE functions, including warnings and errors for each subject. Format varies based on pipeline output.

__________________FROM JESS
The above "varies based on pipeline output" is kind of vague.  Is it not possible to provide an example (even if that that isn't necessary 100% representative)?
__________________FROM JESS

Each file generated follows BIDS naming conventions for file naming: `output_XXX_task_YYY_run_ZZZ.log`

### Pipeline Steps

#### 1) Filter

- High-pass filter the data using MNE function
- Read in the "highPass" "lowpass" fields from the `user_params.json` file to define filter parameters

__________________FROM JESS
Should that be "functions" above?  That feels better to me grammatically, but only if there are, actually, more than one!  Also, is it correct that camelCase was used for "highPass" but not for "lowpass"?
__________________FROM JESS

#### 2) Reject Bad Channels

- Auto-detect and remove bad channels (those that are “noisy” for a majority of the recording)
- Write to output file (field "globalBad_chans") to indicate which channels were detected as bad

#### 3) Independent Component Analysis

  Overview: ICA requires a decent amount of [stationarity](https://towardsdatascience.com/stationarity-in-time-series-analysis-90c94f27322#:~:text=In%20t%20he%20most%20intuitive,not%20itself%20change%20over%20time.) in the data. This is often violated by raw EEG. One way around this is to first make a copy of the EEG data using automated methods to detect noisy portions of data and removing these sections. ICA is then run on the copied data after cleaning. The ICA weights produced by the copied dataset are copied back into original recording. In this way, we do not have to “throw out” sections of noisy data, while, at the same time, we are able to derive an improved ICA decomposition.

__________________FROM JESS
What are "Prepica" and "Rejica"?  I couldn't find them online and I'm not familiar with the terms.
__________________FROM JESS

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

#### 4) Segment
- Segment by epoch to "cut" the continuous data into epochs of data such that the zero point for each epoch is a given marker of interest
- Write to output file (field "XXX") which markers were used for epoching purposes, how many of each epoch were created, and how many milliseconds were retained before/after the markers of interest

#### 5) Final Reject Epochs
- Loop through each channel. For a given channel, loop over all epochs for that channel and identify epochs for which that channel, for a given epoch, exceeds either the voltage threshold or spectral threshold. If it exceeds the threshold, reject the channel data for this channel/epoch.
- Write to the output file ("field XXX") which channel/epoch intersections were rejected

#### 6) Interpolate
- Interpolate missing channels, at the channel/epoch level, using a spherical spline interpolation, as implemented in MNE
- Interpolate missing channels, at the global level, using a spherical spline interpolation, as implemented in MNE
- Write to output file (field "XXX") which channels were interpolated and using what method

#### 7) Re-reference
- Re-reference the data to the average of all electrodes (“average reference”) using the MNE function
- Write to output file (field "XXX") which data were re-referenced to average

## Work in Development
This `main` branch contains completed releases for this project. For all work-in-progress, please switch over to the `dev` branches.

## Contributors
| Name | Role |
| ---  | ---  |
| insert team member | add team member's role |
| insert team member | add team member's role |
| insert team member | add team member's role |

Learn more about us [here](www.ndclab.com/people).

## Contributing
If you are interested in contributing, please read our [CONTRIBUTING.md](CONTRIBUTING.md) file.

