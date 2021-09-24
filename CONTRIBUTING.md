# PEPPER-Pipeline contributing docs & standards
Welcome to the PEPPER-Pipeline project! To get started on collaborating view the contents below. We welcome contributors from **all** backgrounds! 

The development of the PEPPER-Pipeline is focused on optimizing an automated, flexible, and easy-to-use preprocessing pipeline dedicated to EEG preprocessing (as opposed to MEG).

Following the optimization of import and preprocessing tools, development will focus on building out a common core of EEG processing tools to handle ERP, time-frequency, and source-based analyses. 

## Contents

* [Submit an issue](#Submit-an-Issue)  
* [Create documentation](#Create-documentation)
* [Contribute to the code](#Contribute-to-the-code)
    * [Directory Structure](#Directory-Structure)
    * [Function Standards](#Function-Standards)
* [Pipeline overview](#Pipeline-overview)  
* [Containers](#Containers)
* [Git Workflow](#Git-Workflow)  
* [CI Testing](#Continuous-Integration-Testing)  
* [Reminders](#Reminders)  

## Submit an Issue

If you believe a new issue needs to be added to the [list of open issues](https://github.com/NDCLab/PEPPER-Pipeline/issues):
* Verify that the suggestion does not already exist 
* Use the appropriate issue template

## Create documentation

To be implemented! 

## Contribute to the code

If someone is already assigned to an issue that you intend to work on, post a comment to ask if you can help before assigning yourself.

If you do not receive a response within **24 hours**, then you are free to start work on the issue, but be sure to loop them in on your development plans. 

To get started on coding, follow the listed steps below. Note that you must have a GitHub account to collaborate to this project. All quoted commands are executed in your shell.

1. Fork the repo (replace "user" with your GitHub username). 

```
git clone https://github.com/user/pepper-pipeline.git
cd pepper-pipeline/
```

2. Build and activate a container using the OS relevant files (see `container/README.md`).

3. Switch to the branch that you plan to contribute to. 

  * If work on this issue has already begun, then fetch and checkout the active branch.
  ```
  git fetch
  git checkout dev-feature-issue
  ```

 * If this issue has not begun development, then create a new branch.

  ```
  git checkout -b dev-feature-issue 
  git push origin dev-feature-issue
  ```

4. Create a sub-branch using your name/identifier. 

  ```
  git checkout dev-feature-issue-name 
  ```

5. Implement changes (commit often!).

  ```
  git add file1 file2
  git commit -m "Attached flux capacitor" 
  ```

6. After you complete all your intended commits, push changes to branch.

  ```
  git push origin dev-feature-issue-name
  ```

7. Create a pull-request using the GitHub GUI. 

### Directory Structure
```yml
PEPPER-Pipeline
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

All pipeline functions reside within their respective folders:

#### preprocess
Modules that are part of the pre-processing pipeline.

#### data 
Modules that are part of the creation and reading of data.

### Function Standards

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

## Overview
Please see the roadmap available on the [README.md](README.md) file of this repository.

<img src="https://user-images.githubusercontent.com/26397102/123485629-7820cd80-d5d8-11eb-916f-fa269a7ea05a.png" alt="drawing" width="400"/>

*UML diagram for run, which references to run:preprocess*

<img src="https://user-images.githubusercontent.com/26397102/120357498-22078580-c2cb-11eb-82b8-ab025f29e61a.png" alt="drawing" width="800"/>

*UML diagram for run:preprocess*

The UML diagrams above detail the discrete pipeline steps of the default `user_params.json` file: 

1. `load:data` (pipeline input)

    A subset of raw data described in `load_data` is extracted. Further details on the usage of these parameters are described in the [README](README.md).

2. `run:preprocess`

    The main script calls a series of functions, each one executing a step of the pipeline. Some functions simply utilize an existing MNE function while others are more involved. All, however, follow the same standard format: each feature always receives an EEG object and unpacked variables from the `params` dictionary in the main script. 

    Additionally, each pipeline step returns an EEG object and a dictionary describing the changes that occurred to that EEG object.
    
    Motivation behind each pipeline step is described in the [README.md](README.md). 

3. `write:output`

   At the very last step of the pipeline, each respective output is passed to a `write` module which transforms the summed outputs into a comprehensive file. 

Together, the contents of `user_params.json` and `output_preproc.json` define all details necessary to describe (such as in the methods and results section for a journal publication) the manipulations of the pre-processing pipeline and its outputs.

The long term goal is to automate the writing of these journal article sections via a script that takes "user_params.json" and "output_preproc.json" as inputs. In contrast, the output.log file reflects a much more verbose record of what was run, what the outputs were, and the presence of any warning/errors, etc.

## Containers

Please use the dockerfile & singularity recipe located at `container/`. Directions on installation and usage are located in `container/README.md`. 

## Git Workflow 

![ndcworkflow](https://user-images.githubusercontent.com/26397102/116148813-00512800-a6a7-11eb-9624-cd81f11d3ada.png)

Development is driven by the [feature branch workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow), wherein each new feature is encapsulated in its own branch. This ensures changes are properly tested and integrated before they deploy, while still allowing for development to be done in parallel.

The PEPPER branches follow this convention:

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
To automatically run tests and check for [PEP8](https://www.python.org/dev/peps/pep-0008/) styling, the lab employs [continuous integration](https://www.atlassian.com/continuous-delivery/continuous-integration). 

NDCLab CI documentation is listed [here](https://ndclab.github.io/wiki/docs/technical-docs/python-ci-workflow.html). 

## Reminders
1. Only push directly (without code review) to dev-feature-[featureName]-[yourName].
2. You must initiate a pull request (and assign at least one person) for any higher-level branch.
3. If there is no BIDS standard for a type of file that a feature outputs, the developer should set things up in a way that is in line with [general BIDS principles](https://bids.neuroimaging.io/).
4. Preprocessing functions must follow the function standards listed [above](#Function-Standards).
5. All Python code must follow the [NDClab programming standards](https://ndclab.github.io/wiki/docs/etiquette/programming-standards.html).
