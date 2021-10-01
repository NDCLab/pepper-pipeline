# PEPPER-Pipeline 
Welcome to the PEPPER-Pipeline project! To get started on collaborating view the following [wiki link](https://ndclab.github.io/wiki/docs/technical-docs/pepper-usage.html). 

## General Reminders
1. Only push directly (without code review) to dev-feature-[featureName]-[yourName].
2. You must initiate a pull request (and assign at least one person) for any higher-level branch.
3. If there is no BIDS standard for a type of file that a feature outputs, the developer should set things up in a way that is in line with [general BIDS principles](https://bids.neuroimaging.io/).
4. Preprocessing functions must follow the function standards listed [above](#Function-Standards).
5. All Python code must follow the [NDClab programming standards](https://ndclab.github.io/wiki/docs/etiquette/programming-standards.html).

## Directory Structure
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

### preprocess
Modules that are part of the pre-processing pipeline.

### data 
Modules that are part of the creation and reading of data.

## Function Standards

### preprocess

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

