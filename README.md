# baseEEG
Lab-wide EEG scripts

![baseeegheader](https://user-images.githubusercontent.com/26397102/117209976-b958e600-adbc-11eb-8f23-d6015a28935e.png)

Development guidelines and details are listed in [contributing.md](contributing.md)

## Pipeline Steps

### 1) Feature-filter

- High pass filter the data using mne function
- Read in the the "highPass" "lowpass" fields from the "user_params.json" file to define filter parameters

### 2) Feature-badchans

- auto-detect and remove bad channels (those that are “noisy” for a majority of the recording)
- write to output file to indicate which channels were detected as bad (write to field "globalBad_chans")

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
- segment/epoch (cut) the continuous data into epochs of data, such that the zero point for each epoch is a given marker of interest
- write to output file which markers were used for epoching purposes, how many of each epoch were created, and how many ms appear before/after the markers of interest

### 5) Feature-finalrej
- loop through each channel. For a given channel, loop over all epochs for that channel and identify epochs for which that channel, for a given epoch, exceeds either the voltage threshold or spectral threshold. If it exceeds the threshold, reject the channel data for this channel/epoch.
- write to the output file which channel/epoch intersections were rejected

### 6) Feature-interp
- interpolate missing channels, at the channel/epoch level using a spherical spline interpolation, as implemented in mne
- interpolate missing channels, at the global level, using a spherical spline interpolation, as implemented in mne
- write to output file which channels were interpolated and using what method

### 7) Feature-reref
- re-reference the data to the average of all electrodes (“average reference”) using the mne function
- write to output file that data were re-referenced to average

## Input/Output Files

The pipeline reads from a user-supplied json file called [user_params.json](#user_params.json) and writes to many output files called [output_preproc.json](#output_preproc.json) and [output.log](#output_sub.log) for each subject

Together, the contents of [user_params.json](#user_params.json) and [output_preproc.json](#output_preproc.json) define all details neccesary to write relevant methods and results section for a journal publication to describe what the preprocessing pipeline did and what the outputs were

The long term goal is to automate the writing of these journal article sections via a script that takes "user_params.json" and "output_preproc.json" as inputs. In contrast, the output.log file reflects a much more verbose record of what was run, what the outputs were, and the pressence of any warning/errors, etc

### user_params.json

This singular input file defines all research-relevant features of the pipeline. The user may define these paremeters within the JSON file to infuence filtering and channel rejection

Format:
```javascript
{
    "highPass": [.3],
    "lowpass": [50]
}
```

### output_preproc.json

These output files will contain all research-relevant outputs of the pipeline (e.g. # bad channels rejected, # ICA artifacts rejected, etc.). This file will be built iteratively as the pipeline progresses

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


