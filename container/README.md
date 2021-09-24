# Singularity and Docker
The images described below are container files that all have the base functionality required for reliably running, testing, and developing the PEPPER pipeline. This includes Python, MNE, Pandas, and more.

# Docker

## Pulling Existing Container


## Building New Container

## How to Use Docker? 
With a Dockerfile, we can construct a docker container with a volume attached to it. To begin using docker: 
1. Download and install Docker on your local PC (https://docs.docker.com/get-docker/). If using Windows 10 Home, downloading WSL2 is necessary. 
2. Pull the latest Dockerfile and environment.yml from the github repository.
3. Begin building the docker file with a specific tag, expressed as
   `
   docker build -t [tag] .  
   `
   where: 
    * The docker build builds docker images from a Dockerfile
    * The -t flag tags our image. This is simply a human-readable name for the final image.
    * . tells docker should look for the Dockerfile in the current directory. 
4. We can now create a docker volume called data. To create the volume, we run `docker volume create data`, resulting in a volume called data. When we run `docker volume ls`, we should get the following output
   ```bash
    DRIVER    VOLUME NAME
    local     data
   ```
   which lists all of the volumes known to docker. If we want to see detailed information on the docker container, we can use the inspect command. That is, `docker inspect data` which will produce the following output: 
   ```json 
    [
        {
            "CreatedAt": "2021-04-17T03:53:57Z",
            "Driver": "local",
            "Labels": {},
            "Mountpoint": "/var/lib/docker/volumes/data/_data",
            "Name": "data",
            "Options": {},
            "Scope": "local"
        }
    ]
   ```
5. To mount a data volume to a container, we add the --mount flag to the docker run command. This will allow us to add the volume to the specified container, storing the data produced inside the virtual environment. To run a container and mount a data volume to it, while routing it to some port, such as port 5000, we use the following syntax:
   ```bash 
    docker run --name=[containerName] -it -w /projects -p 5000:8888 --mount source=[volume_name], destination=[docker_image_path] [tag]
   ```
   where: 
    * --name defines a name for the container. 
    * -it tells Docker we want an interactive session with a tty attached. 
    * -w specifies the working directory inside the container 
    * -p maps a network port to the contaiiner 
    * --mount tells docker we want to mount the volume onto the container. 
    * source is the source of the mount. For named volumes, this is the name of the volume. 
    * destination takes as its value the path where the file or directory is mounted in the container. 

    For example, using our previous volume called data and a docker image called anaconda, we can launch a container with the name mini and mount our data volume to it. Consider the following: 
    ```bash
    docker run --name=mini -it -w /projects -p 5000:8888 --mount source=data,destination=/home/ubuntu/data anaconda
    ```

    which will now construct a new container mapped to port 5000 with a volume attached to it. This volume, data, is now mounted on /home/ubuntu/data.

6. Once the volume is attached to the container, we can use the docker cp command to copy data from the host to the container. This also works interchangeably. To copy a file from the local file system to a container, the syntax is as follows: 
   ```bash 
    docker cp <src-path> <container>:<dest-path>
   ```
   and to copy a file from the container to the file system, it is expressed as
   ```bash 
    docker cp <container>:<src-path> <local-dest-path>
   ```

   Therefore, to copy a data set from your host machine to a volume within your docker container, we do
   ```bash
    docker cp "datatset\path\name" mini:"/home/ubuntu/data"
   ```
7. Run a container instance as a root by executing 

   ```bash
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