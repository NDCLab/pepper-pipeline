# baseEEG
Lab-wide EEG scripts

If working on development for this project, please use the docker image located at `base_eeg_docker_files/`. Directions on installation and usage located in `base_eeg_docker_files/readme.txt`. 



## Issues

See issues for current/future work. 

Always assign yourself to an issue before beginning work on it!

If someone is already assigned to an issue, but you want to help, post a comment to ask if you can help before assigning yourself. If no response within 24 hours, then you are free to start work on the issue, but post another comment first to let them know what you will be doing.



## Git Workflow 

![ndcworkflow](https://user-images.githubusercontent.com/26397102/114767588-6e076680-9d2d-11eb-87a7-0f1a48d9984f.png)

Folder/branch organization should follow this convention:

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



## Roadmap
- See issues for latest roadmap

Folder/branch organization should follow this convention:

main

->dev

-->dev-feature-[featureName]

--->dev-feature-[featureName]-[yourName]

Reminders:

1. only push directly (without code review) to dev-feature-[featureName]=[yourName]
2. Must initiate pull request (and assign at least one person) for any higher-level branch
3. Mandatory code review by one person for all pull requests 
4. main should be 100% stable and deployable/usable by any lab member (i.e. must also have full documentation and no "test features")
5. dev is the must up-to-date, complete version of the code, including all tested features, though dev is considered alpha/beta
6. dev-feature-[featureName] reflects a branch devoted to development/testing of a particular feature. Likely not stable, but at least has been reviewed by a second author



## Example Files for Development
- Two example files are currently being used for development:
- For feature-io, we are using this file here: https://drive.google.com/file/d/1-e0-AryZRDmgzXyJtm27vWFq48FY_lUj/view?usp=sharing.
- For all preprocessing features, we are using this file here: https://osf.io/cj2dr/ (use data located in: eeg_matchingpennies->sub-05->eeg

