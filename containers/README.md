# Singularity and Docker
The content below describes how to build, pull, and develop the container files required for reliably running the PEPPER pipeline. 

# Docker

The docker container image used for this project can be simply pulled from [Docker Hub](https://hub.docker.com/) as described in the section [Pulling an Existing Container](#Pulling-an-Existing-Container). However, if you are planning on expanding this project to include additional packages, then you must rebuild the container image with your new configurations as described in the section [Building a New Container](#Building-a-New-Container).

Both approaches will require an installation of [Docker Desktop](https://www.docker.com/products/docker-desktop). To install, follow the [these directions](https://docs.docker.com/get-docker/). 

Once Docker is installed to your computer, open the "Docker Desktop" application. 

## Pulling an Existing Container

To work with an existing PEPPER container simply use the `pull` command exactly as described below:
   ```
   docker pull fsaid22/pepper_container:latest
   ```

## Building a New Container

To build a new docker file with a specific tag executing the following command within the *PEPPER-pipeline* root directory: 
   ```
   docker build -t [tag] container/Dockerfile
   ```

## Binding Data & Running

Once the container has been built or pulled, a volume must be created and bound in order to transfer programs and data into the container. Once that is successfully completed, the container can be used to run all features of *PEPPER*:

1. Create a docker volume named *data* to initialize the volume:
   ```
   docker volume create data
   ```

2. Bind the volume by running the container with the specified tags:
   ```
   docker run --name pepper -it -d -w /projects --mount source=data,destination=/projects fsaid22/pepper_container
   ```

3. Copy data from the host to the container using the `cp` command:
   ```
   docker cp ../../scripts pepper:/projects
   docker cp ../../run.py pepper:/projects
   docker cp ../../conftest.py pepper:/projects
   docker cp ../../CONTRIBUTING.md pepper:/projects
   docker cp ../../README.md pepper:/projects
   docker cp ../../user_params.json pepper:/projects
   docker cp ../../.github pepper:/projects
   ```

4. Run a container instance as a root by executing:
   ```
   docker exec -u root -it pepper bash
   ```

# Singularity

As there is currently no central repository of Singularity container images, the image must be built from the `eeg-pipe.recipe` file. 

The image must be built in a Linux environment with root access, as Singularity is only compatible for Linux environments and permissions outside of the container will be mirrored to inside of the container. This means that unless you are an administrator on your HPC, you must build this container in a local environment before moving it to your cluster.

To install Singularity to a Linux OS, follow [these instructions](https://sylabs.io/guides/3.0/user-guide/installation.html).

Once singularity is installed, confirm the installation by running:
```
singularity --version
```

Once that is confirmed, proceed with the following steps to build the image:

1. Navigate to the container folder and build the container image using the `build` command. The build time will depend on the container size, with large containers taking more time to build. 
   ```
   cd container
   sudo singularity build pepper-container.simg eeg-pipe.recipe
   ```

2. If you are planning to use this container image on a cluster, export the container file to your cluster using your preferred means of data-transfer. Once that is complete, navigate to your cluster's login node. 

3. To interact with a shell instance of the container image, execute the `shell` command:
   ```
   singularity shell container/pepper-container.simg.simg
   ```

Additionally, if you would like to bind specific data paths to the container, execute the above `shell` command with the `--bind` tag:
```
singularity shell --bind [path]/[to]/[data],[path]/[to]/[data2] container/pepper-container.simg.simg
```

4. To find out more about the functionality of Singularity, view the following [documentation](https://sylabs.io/guides/3.0/user-guide/quick_start.html).