# baseEEG
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
Lab-wide EEG scripts

![baseeegheader](https://user-images.githubusercontent.com/26397102/117209976-b958e600-adbc-11eb-8f23-d6015a28935e.png)

Development guidelines and details are listed in [contributing.md](contributing.md)

## Usage

This project comes with a default `user_params.json` file which directly controls the order of pipeline steps and their parameters:

```json
{
    "data": {
        "Bids_data_root": "PATH"
    },
    "preprocess": {
        "filter": {
            "param1": "VALUE"
        },
        "segment_data": {
            "param1": "VALUE",
            "param2": "VALUE"
        },
        "final_reject_epoch": {
        }, 
        "interpolate_data": {
            "param1": "VALUE"
        }
    }
}
```

To influence parameters, which functions are called, and in which order, edit this file.

Run `run.py` to interpret this file and output cleaned EEG data.  
## Output 

### output_preproc.json

These output files will contain all research-relevant outputs of the pipeline (e.g. # bad channels rejected, # ICA artifacts rejected, etc.). This file will be built iteratively as the pipeline progresses.

Each file name generated on a subject will follow the BIDS naming standard: `output_preproc_XXX_task_YYY_run_ZZZ.json`

Format:
```javascript
{
    "globalBad_Chans": [1, 23, 119],
    "icArtifacts": [1, 3, 9]
}
```

### output_sub.log

These output log files will define the verbose outputs of mne functions including warnings and errors for each subject. Format will vary based on pipeline output

Each file name generated on a subject will follow the BIDS naming standard: `output_XXX_task_YYY_run_ZZZ.log`

## Pipeline Steps

### 1) Feature-filter

- High pass filter the data using mne function
- Read in the the "highPass" "lowpass" fields from the "user_params.json" file to define filter parameters

### 2) Feature-badchans

- Auto-detect and remove bad channels (those that are “noisy” for a majority of the recording)
- Write to output file to indicate which channels were detected as bad (write to field "globalBad_chans")

### 3) Feature-ica

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

### 4) Feature-segment
- Segment/epoch (cut) the continuous data into epochs of data, such that the zero point for each epoch is a given marker of interest
- Write to output file which markers were used for epoching purposes, how many of each epoch were created, and how many ms appear before/after the markers of interest

### 5) Feature-finalrej
- Loop through each channel. For a given channel, loop over all epochs for that channel and identify epochs for which that channel, for a given epoch, exceeds either the voltage threshold or spectral threshold. If it exceeds the threshold, reject the channel data for this channel/epoch.
- Write to the output file which channel/epoch intersections were rejected

### 6) Feature-interp
- Interpolate missing channels, at the channel/epoch level using a spherical spline interpolation, as implemented in mne
- Interpolate missing channels, at the global level, using a spherical spline interpolation, as implemented in mne
- Write to output file which channels were interpolated and using what method

### 7) Feature-reref
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
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!