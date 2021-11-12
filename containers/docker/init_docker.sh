#!/bin/bash

# create data volume
docker volume create data

# bind the volume by running the container with the specified tags
docker run -it -d --name pepper -w /projects/pepper-pipeline --mount source=data,destination=/projects $1

# copy all data from local to container
docker cp ../../scripts pepper:/projects/pepper-pipeline
docker cp ../../run.py pepper:/projects/pepper-pipeline
docker cp ../../CONTRIBUTING.md pepper:/projects/pepper-pipeline
docker cp ../../README.md pepper:/projects/pepper-pipeline
docker cp ../../user_params.json pepper:/projects/pepper-pipeline

# copy in git metadata
docker cp ../../.github pepper:/projects/pepper-pipeline
docker cp ../../.git pepper:/projects/pepper-pipeline
docker cp ../../.gitignore pepper:/projects/pepper-pipeline

# run container instance
docker exec -u root -it pepper bash
