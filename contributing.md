# baseEEG contributing docs & standards
Welcome to baseEEG! The guidelines for development are as follows: 

* [Roadmap](#Roadmap)  
* [Containers](#Containers)
* [Issues](#Issues)  
* [Git-Workflow](#Git-Workflow)  
* [CI-test](#CI-test)  
* [Input-Data](#Example-Data)  
* [Output-Data](#Output-Data)
* [Reminders](#Reminders)  


## Roadmap

![pipelineUMLverdana](https://user-images.githubusercontent.com/26397102/117684554-b96d3300-b17a-11eb-9b6c-0013e032331d.png)

The UML diagram listed above details the pipeline steps that run for each subject:

### Pipeline Input (load_data)
- [raw EEG data](#Example-Data)  
- [user_params.json](README.md)
    ```json
    {
        "filter": {
            "highPass": [0.3],
            "lowpass": [50]
        }, 
        "segment": {
            "tmin": [-0.2],
            "tmax": [0.5]
        }
    }
    ```
    Details a series of parameters that the user defines.

### Main Script 

The main script calls a series of functions, each one executing a step of the pipeline. Some simply utilize an existing mne function, while others are more involved, but they all follow the same standard format: each feature always receives the params dictionary and data from the main script. Detail on pipeline steps listed in the [readme.md](README.md). 

Each feature function finishes by returning a dictionary of pipeline outputs.

### Pipeline Output (output_preproc)
At the very last step of the pipeline, each respective output is passed to the `output_preproc` function which transforms the summed outputs into a comprehensive file. Detailed in [readme.md](README.md)
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


## Example-Data
- [BIDS.zip](https://drive.google.com/drive/u/0/folders/1aQY97T9EfkPEkuiCav2ei9cs0DFegO4-) is used as the test input file for all pipeline feature development. 


## Reminders
1. only push directly (without code review) to dev-feature-[featureName]-[yourName]
2. Must initiate pull request (and assign at least one person) for any higher-level branch
3. Mandatory code review by one person for all pull requests 
4. If there is no BIDS standard for a type of file that a feature outputs, the developer should set things up in a way that is in line with [general BIDS principles](https://www.nature.com/articles/s41597-019-0104-8).
