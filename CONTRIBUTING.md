# baseEEG contributing docs & standards
Welcome to baseEEG! The guidelines for development are as follows: 

* [Roadmap](#Roadmap)  
    * [Overview](#Overview)
    * [Structure](#Directory-Structure)
    * [Function-Standards](#Function-Standards)
* [Containers](#Containers)
* [Issues](#Issues)  
* [Git-Workflow](#Git-Workflow)  
* [CI-test](#CI-test)  
* [Output-Data](#Output-Data)
* [Reminders](#Reminders)  


## Roadmap

### Overview 

![UMLrawread](https://user-images.githubusercontent.com/26397102/119166320-1642d600-ba24-11eb-8dd6-0d35430831b0.png)

The UML diagram listed above details the pipeline steps that run for each subject:

1. Pipeline Input (load_data)
- [raw EEG data](#Example-Data)  
- [user_params.json](README.md)

2. Main Script

    The main script calls a series of functions, each one executing a step of the pipeline. Some simply utilize an existing mne function, while others are more involved, but they all follow the same standard format: each feature always receives an EEG object and unpacked variables from the params dictionary from the main script. 

    Additionally, each pipeline step will likewise return an EEG object and a dictionary describing the changes that occured to that EEG object.

    Motivation behind each pipeline step listed in the [readme.md](README.md). 

3. Pipeline Output

   At the very last step of the pipeline, each respective output is passed to the `output_preproc` function which transforms the summed outputs into a comprehensive file. 
- [output_preproc.json](README.md)
- [output.log](README.md)

Together, the contents of [user_params.json](#user_params.json) and [output_preproc.json](#output_preproc.json) define all details neccesary to write relevant methods and results section for a journal publication to describe what the preprocessing pipeline did and what the outputs were.

The long term goal is to automate the writing of these journal article sections via a script that takes "user_params.json" and "output_preproc.json" as inputs. In contrast, the output.log file reflects a much more verbose record of what was run, what the outputs were, and the pressence of any warning/errors, etc.


### Directory-Structure
```yml
baseEEG
├── run.py
├── user_params.json
├── scripts
|    ├──__init__.py
|    ├──data
|    |    ├──__init__.py
|    |    ├──data_load.py
|    |    ├──data_write.py
|    ├──postprocess
|    |    ├──__init__.py
|    |    ├──postprocess.py
|    ├──preprocess
|    |    ├──__init__.py
|    |    ├──preprocess.py
```
All pipeline functions reside within their respective modules. For example, functions that are part of the preprocessing pipeline reside in `preprocess.py`, while functions that are part of postprocessing reside in `postprocess.py`.

### Function-Standards 

#### preprocess

All functions for the preprocessing pipeline must contain the following parameter list and return values to satisfy `run.py` constraints.
```python
def preprocess_step(EEG_object, [user_param1, user_param2, ...]):
     """Function description
    Parameters
    ----------
    EEG_object: EEG_object type
            description
    user_param1:    type
                    description
    user_param2:    type
                    description
    ...

    Throws
    ----------
    What errors are thrown if anything

    Returns
    ----------
    EEG_object_modified:    EEG_object_modified type
                            description
    output_dictionary:  dictionary
                        description of annotations 
    """
    # code to do pipeline step

    return EEG_object_modified, output_dict 
```

## Containers

Please use the docker image located at `base_eeg_docker_files/`. Directions on installation and usage located in `base_eeg_docker_files/README.md`. 


## Issues

See issues for current/future work. 

Always assign yourself to an issue before beginning work on it!

If someone is already assigned to an issue that you intend to work on, post a comment to ask if you can help before assigning yourself. If no response within 24 hours, then you are free to start work on the issue, but post another comment first to let them know what you will be doing.


## Git-Workflow 

![ndcworkflow](https://user-images.githubusercontent.com/26397102/116148813-00512800-a6a7-11eb-9624-cd81f11d3ada.png)

Development is driven by the [feature branch workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow), where each new feature is encapsulated in a branch. This ensures changes are properly tested & integrated while still allowing for development to be done in parallel.

Subsequently, branches follow this convention:

`main`
- No test features
- 100% stable and usable by any lab members 
- *No direct commits*

`->dev`
- Up to date development branch with properly tested/reviewed features 
- *No direct commits*

`-->dev-feature-[featureName]`
- Ongoing development and testing of feature to be pull requested into `dev` 
- *No direct commits*

`--->dev-feature-[featureName]-[yourName]`
- *Only* branch available for personal development, must be branched off of `-->dev-feature-[featureName]` branch
- Merged into `-->dev-feature-[featureName]` after pull-request (code review)


## CI-test
[NDCLab CI test documentation](https://docs.google.com/document/d/1lTYCLn6XK4Ln-BjcNhMMqpQFhYWg6OHB/edit)

## Example-Data
- [BIDS.zip](https://drive.google.com/drive/u/0/folders/1aQY97T9EfkPEkuiCav2ei9cs0DFegO4-) is used as the test input file for all pipeline feature development. 


## Reminders
1. Only push directly (without code review) to dev-feature-[featureName]-[yourName]
2. Must initiate pull request (and assign at least one person) for any higher-level branch
3. Mandatory code review by one person for all pull requests 
4. If there is no BIDS standard for a type of file that a feature outputs, the developer should set things up in a way that is in line with [general BIDS principles](https://www.nature.com/articles/s41597-019-0104-8).