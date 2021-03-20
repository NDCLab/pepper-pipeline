# baseEEG
lab-wide EEG scripts

If working on development for this project, please use the baseEEG docker image located in this repo

See issues for current/future work

Always assign yourself to an issue before beginning work on it!

Example file to use for development is located here: https://drive.google.com/file/d/1-e0-AryZRDmgzXyJtm27vWFq48FY_lUj/view?usp=sharing
-Must request access to the folder first; requires appropriate onboarding to guaruntee ethicical use of data.

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



Roadmap

2. Push initial jupyter notebook. all set up to sync to this repo and work off this same notebook
3. code for first step of pipeline: import example mff data and then write as bids data. WHoever, does this first, everyone else follow the file path naming conventions
4.proceed through each step of the mne python tutorial, with each step viewed as an additional "feature" and an issue created for it.
5.
