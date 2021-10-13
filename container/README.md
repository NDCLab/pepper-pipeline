# Singularity and Docker
The content described below are container files that all have the base functionality required for reliably running, testing, and developing the PEPPER pipeline. These include Python, MNE, Pandas, and more.

# Docker

The docker container image used for this project can be simply pulled from [Docker Hub](https://hub.docker.com/) as described in the section *Pulling Existing Container*. However, if you are planning on expanding the project to include additional Python packages, then you must rebuild the container image with your additional configurations as described in the section *Building a New Container*.

Both approaches will require [Docker Desktop](https://www.docker.com/products/docker-desktop). To install, follow the [these directions](https://docs.docker.com/get-docker/). 

Once Docker is installed to your computer, verify the installation by opening the "Docker Desktop" application. 

## Pulling Existing Container

To work with the existing PEPPER container simply use the `pull` command:
   ```
   docker pull fsaid22/pepper_container:latest
   ```

## Building a New Container

Build the new docker file with a specific tag, by executing
   ```
   docker build -t [tag] container/Dockerfile
   ```

## Binding Data & Running

Once the container has been built or pulled, a volume must be created and binded in order to transfer programs and data into the container. Once that is successfully completed, the container can be reliably run as described below: 

1. Create a docker volume to bind data and scripts to the container:
   ```
   docker volume create data
   ```

2. Bind the volume by running the container with the specified tags:
   ```
    docker run --name=[containerName] -it -w /projects --mount source=[volume_name], destination=[docker_image_path] [tag]
   ```

3. Copy data from the host to the container using the `cp` command:
   ```
   docker cp <src-path> <container>:<dest-path>
   ```

4. Run a container instance as a root by executing:
   ```
   docker exec -u root -it [containerName] bash
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