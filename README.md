# baseEEG
Lab-wide EEG scripts

If working on development for this project, please use the docker image located at `base_eeg_docker_file/`. Directions on installation and usage located in `base_eeg_docker_files/readme.txt`. 



## Issues

See issues for current/future work. 

Always assign yourself to an issue before beginning work on it!

Example file to use for development is located here: https://drive.google.com/file/d/1-e0-AryZRDmgzXyJtm27vWFq48FY_lUj/view?usp=sharing. Must request access to the folder first; requires appropriate onboarding to guaruntee ethicical use of data.


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

`--->dev-feature-[featureName]-[yourName]`
- *only* branch available for personal development, must be branched off of `-->dev-feature-[featureName]` branch
- Merged into `-->dev-feature-[featureName]` after pull-request (code review)



## Roadmap

1. Solve the issue of jupyter notebooks and github. implement solution and communicate to group
2. Push initial jupyter notebook. all set up to sync to this repo and work off this same notebook
3. code for first step of pipeline: import example mff data and then write as bids data. WHoever, does this first, everyone else follow the file path naming conventions
4. proceed through each step of the mne python tutorial, with each step viewed as an additional "feature" and an issue created for it.
5. ... 
