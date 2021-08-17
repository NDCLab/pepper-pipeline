# Contributing to baseEEG

## Overview
Welcome to baseEEG! Note that the development of baseEEG is focused on optimizing an automated, flexible, and easy-to-use pre-processing pipeline dedicated to EEG (as opposed to MEG) pre-processing. Additionally, there is an unofficial script template for converting EEG data to BIDS format (heavily leveraging MNE-BIDS). Following the optimization of import and pre-processing tools, development will focus on building out a common core of EEG processing tools to handle ERP, time-frequency, and source-based analyses. The guidelines for development are as follows:

* [Overview](#Roadmap)  
    * [EEG to BIDS](#EEG-BIDS)
    * [Directory Structure](#Directory-Structure)
    * [Function Standards](#Function-Standards)
* [Containers](#Containers)
* [Issues](#Issues)  
* [Git Workflow](#Git-Workflow)  
* [CI Testing](#Continuous-Integration-Testing)  
* [Output Data](#Output-Data)
* [Reminders](#Reminders)  

## Overview
Please see the roadmap available on the [README.md](README.md) file of this repository.

<img src="https://user-images.githubusercontent.com/26397102/123485629-7820cd80-d5d8-11eb-916f-fa269a7ea05a.png" alt="drawing" width="400"/>

*UML diagram for run, which references to run:preprocess*

<img src="https://user-images.githubusercontent.com/26397102/120357498-22078580-c2cb-11eb-82b8-ab025f29e61a.png" alt="drawing" width="800"/>

*UML diagram for run:preprocess*

The UML diagrams above detail the discrete pipeline steps of the default `user_params.json` file: 

1. `load:data` (pipeline input)

    A subset of raw data described in `load_data` of `user_params.json` is extracted. The parameters and discrete pipeline steps are likewise extracted. Further details on the usage of these parameters are described in the [README](README.md).

2. `run:preprocess`

    The main script calls a series of functions, each one executing a step of the pipeline. Some functions simply utilize an existing MNE function while others are more involved. All, however, follow the same standard format: each feature always receives an EEG object and unpacked variables from the `params` dictionary in the main script. 

    Additionally, each pipeline step returns an EEG object and a dictionary describing the changes that occurred to that EEG object.
    
    Motivation behind each pipeline step is described in the [README.md](README.md). 

3. `write:output`

   At the very last step of the pipeline, each respective output is passed to a `write` module function which transforms the summed outputs into a comprehensive file. 

Together, the contents of `user_params.json` and `output_preproc.json` define all details necessary to describe (such as in the methods and results section for a journal publication) the manipulations of the pre-processing pipeline and its outputs.

The long term goal is to automate the writing of these journal article sections via a script that takes "user_params.json" and "output_preproc.json" as inputs. In contrast, the output.log file reflects a much more verbose record of what was run, what the outputs were, and the presence of any warning/errors, etc.

### EEG-BIDS


### Directory-Structure
```yml
baseEEG
├── run.py
├── user_params.json
├── scripts
|    ├──__init__.py
|    ├──data
|    |    ├──__init__.py
|    |    ├──load.py
|    |    ├──write.py
|    ├──postprocess
|    |    ├──__init__.py
|    |    ├──postprocess.py
|    ├──preprocess
|    |    ├──__init__.py
|    |    ├──preprocess.py
```
The `scripts` directory is the local [package](https://docs.python.org/3/tutorial/modules.html#packages) where sub-packages & modules will be written. This ensures that modules are neatly divided according to responsibility, which helps with parallel development and debugging. 

All pipeline functions reside within their respective modules. For example, functions that are part of the pre-processing pipeline reside in `preprocess.py`, while functions that are part of post-processing reside in `postprocess.py`.

### Function Standards

__________________FROM JESS
Is this section going to have the other "data" and "postprocess" information?  If so, it might be helpful (for new visitor navigation) to add the headers and just include "Details to come soon."
__________________FROM JESS

#### preprocess

All functions for the pre-processing pipeline must contain the following parameter list and return values to satisfy `run.py` constraints.

In addition, function documentation must include the following class comments as specified by the [NDClab programming standards](https://ndclab.github.io/wiki/docs/etiquette/programming-standards.html#python). 
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

Please use the dockerfile & singularity recipe located at `container/`. Directions on installation and usage are located in `container/README.md`. 


## Issues

See the [list of open issues](https://github.com/NDCLab/baseEEG/issues) for current and future work to be performed.

Always assign yourself to an issue before beginning work on it!

If someone is already assigned to an issue that you intend to work on, post a comment to ask if you can help before assigning yourself. If you do not receive a response within 24 hours, then you are free to start work on the issue, but first post another comment to let them know what you will be doing on the issue.

If you believe a new issue needs to be added to the [list of open issues](https://github.com/NDCLab/baseEEG/issues):
* Verify that the problem/suggestion does not already have an issue logged in GitHub.
* Use the appropriate issue template to submit the problem/suggestion for review.

## Git Workflow 

![ndcworkflow](https://user-images.githubusercontent.com/26397102/116148813-00512800-a6a7-11eb-9624-cd81f11d3ada.png)

Development is driven by the [feature branch workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow), wherein each new feature is encapsulated in its own branch. This ensures changes are properly tested and integrated before they deploy, while still allowing for development to be done in parallel.

The baseEEG branches follow this convention:

`main`
- Represents a stable release, merged from `dev` via a [Level 2 PR review](https://ndclab.github.io/wiki/docs/etiquette/github-etiquette.html#terminology)
- *No direct commits*

`->dev`
- Up-to-date development branch representing an unfinished release
- *No direct commits*

`-->dev-feature-[featureName]`
- Ongoing development and testing of a specific feature that will ultimately be merged into `dev` via a [Level 2 PR review](https://ndclab.github.io/wiki/docs/etiquette/github-etiquette.html#terminology)
- *No direct commits*

`--->dev-feature-[featureName]-[yourName]`
- *Only* branch available for personal development
- Must be branched off the `-->dev-feature-[featureName]` branch
- Merged into `-->dev-feature-[featureName]` via a [Level 1 PR review](https://ndclab.github.io/wiki/docs/etiquette/github-etiquette.html#terminology)


## Continuous Integration Testing
[NDCLab CI test documentation](https://ndclab.github.io/wiki/docs/technical-docs/python-ci-workflow.html)

## Example-Data

- [BIDS.zip](https://drive.google.com/drive/u/0/folders/1aQY97T9EfkPEkuiCav2ei9cs0DFegO4-) is used as the test input file for all pipeline feature development.

__________________FROM JESS
Should we move this zip over to GitHub?  Or it's too big?
__________________FROM JESS


## Reminders
1. Only push directly (without code review) to dev-feature-[featureName]-[yourName].
2. You must initiate a pull request (and assign at least one person) for any higher-level branch.
3. If there is no BIDS standard for a type of file that a feature outputs, the developer should set things up in a way that is in line with [general BIDS principles](https://bids.neuroimaging.io/).

__________________FROM JESS
Would this be a better link for general BIDS principles?
https://bids.neuroimaging.io/

Should we add a reminder about naming conventions and programming standards (with wiki links) to the Reminders section?
__________________FROM JESS
