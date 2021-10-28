:: create data volume
docker volume create data

:: bind the volume by running the container with the specified tags
docker run -it -d --name pepper -w /projects --mount source=data,destination=/projects fsaid22/pepper_container

:: copy all data from local to container
docker cp ../../scripts pepper:/projects
docker cp ../../run.py pepper:/projects
docker cp ../../conftest.py pepper:/projects
docker cp ../../CONTRIBUTING.md pepper:/projects
docker cp ../../README.md pepper:/projects
docker cp ../../user_params.json pepper:/projects
docker cp ../../.github pepper:/projects

:: run container instance
docker exec -u root -it pepper bash