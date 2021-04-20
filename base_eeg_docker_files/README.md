# Containerization 
Containerization is an alternative or companion to virtualization. It involves encapsulating or packaging up software and all its dependencies so that it can run uniformly and consistently on any infrastructure. This allows for developers to create and deploy applications faster and more securely. The image built using the dockerfile has all the base functionality required for analysis, such as Python, MNE, Nipype, TensorFlow, Pandas, and more.  


## What is Docker?

Docker is a set of platform as a service product that uses OS-level virtualization to deliver software in packages called containers. Containers are isolated from one another and bundle their own software, libraries, and configuration files. 

## What is a Docker Volume? 
Docker volumes are the preferred mechanism for persisting data generated 
by and used by Docker containers. While bind mounts are dependent on the 
directory structure and OS of the host machine, volumes are completely 
managed by Docker. Volumes have several advantages over bind mounts: 
* Volumes are easier to back up or migrate than bind mounts.
* Volumes on Docker Desktop have much higher performance than bind mounts from Mac and Windows hosts.
* Volumes can be more safely shared among multiple containers.

Volumes are often a better choice than persisting data in a container’s writable layer, because a volume does not increase the size of the containers using it, and the volume’s contents exist outside the lifecycle of a given container. 


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
   which lists all of the volumes known to docker. If we want to see detailed information on the docker containerr, we can use the inspect command. That is, `docker inspect data` which will produce the following output: 
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
   


<!-- The image built using the code has all the base functionality required for analysis (python, mne, nipype, tensor flow, pandas etc.) you would just need to set your own local directories yourself at this time in order to save work between sessions.
Download and install Docker on your local PC. 
From GitHub pull the latest Dockerfile from the repo as well as the requirements.txt file
While in the directory of the docker file:
docker build -t imageName:version .
#image name is how you will call the image in the future
After the docker image is built, the image can be run and developed on interactivly
docker run -it imageName:version bash


 As for using a local directory with docker the following command works: docker run --rm -it -v $(PWD):/projects -w /projects dockerImage:Version bash

 Note on how to use jupyter in browser mode: to enable in browser jupyter you have to give port access with -p so run this: docker run --rm -it -v $(PWD):/projects -w /projects -p 8888:8888 dockerImage:version bash
then you need to link ports by inputing the following while in the ubuntu docker
jupyter notebook --ip 0.0.0.0 --no-browser --allow-root
finally you can use the browser jupyter by typing the url: localhost:8888/tree on your local browser -->