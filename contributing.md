# baseEEG contributing docs & standards
Welcome to baseEEG! The guidelines for development are as follows: 

* [Roadmap](#Roadmap)  
* [Containers](#Containers)
* [Issues](#Issues)  
* [Git-Workflow](#Git-Workflow)  
* [CI-test](#CI-test)  
* [Input-Data](#Input-Data)  
* [Output-Data](#Output-Data)
* [Reminders](#Reminders)  

## Roadmap

All features (pipeline steps) can be worked on independently and in parallel. Any steps for which implementation relied on a prior step first being completed have been merged into one single feature (e.g., feature-ica contains three steps that must be implemented sequentially). Please self-assign to any feature, read the relevant documentation, reach out with questions, and begin implementation. There is no correct order to implement any of these steps.

The Preprocessing pipeline assumes that data is already in BIDS format. Thus, any scripts (e.g. feature-filter-io) to convert data to BIDS format are NOT part of the preprocessing pipeline. Thus, all steps of the preprocessing pipeline should be written in such a way as to assume a BIDS folder structure file already exists and that standard BIDS metadata files exist (which can be read in to govern preprocessing). 

## Containers

Please use the docker image located at `base_eeg_docker_files/`. Directions on installation and usage located in `base_eeg_docker_files/README.md`. 

## Issues

See issues for current/future work. 

Always assign yourself to an issue before beginning work on it!

If someone is already assigned to an issue that you intend to work on, post a comment to ask if you can help before assigning yourself. If no response within 24 hours, then you are free to start work on the issue, but post another comment first to let them know what you will be doing.

## Git-Workflow 

![ndcworkflow](https://user-images.githubusercontent.com/26397102/116148813-00512800-a6a7-11eb-9624-cd81f11d3ada.png)

Development is driven by the [feature branch workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow), where each new feature is encapsulated in a branch. This ensures changes are properly tested & integrated while still allowing for development to be done in parallel

Subsequently, branches follow this convention:

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

## CI-test
[NDCLab CI test documentation](https://docs.google.com/document/d/1lTYCLn6XK4Ln-BjcNhMMqpQFhYWg6OHB/edit)

## Input-Data
- [BIDS.zip](https://drive.google.com/drive/folders/1aQY97T9EfkPEkuiCav2ei9cs0DFegO4-?usp=sharing) is used as the test input file for all pipeline feature development. 
- [user_params.json](README.md)

## Output-Data
- [output_preproc.json](README.md)
- [output.log](README.md)
    To record function output to log-file, insert the following:
    ```python 
    # initialize log-file
    logging.basicConfig(filename=subject_file_name, filemode='a', encoding='utf-8', level=logging.NOTSET)

    # ... pipeline steps execute ...

    logging.info("describe output of pipeline")
    # record pipeline output
    logging.info(mne.post.info)
    ```

## Reminders
1. only push directly (without code review) to dev-feature-[featureName]-[yourName]
2. Must initiate pull request (and assign at least one person) for any higher-level branch
3. Mandatory code review by one person for all pull requests 
4. If there is no BIDS standard for a type of file that a feature outputs, the developer should set things up in a way that is in line with [general BIDS principles](https://www.nature.com/articles/s41597-019-0104-8).
