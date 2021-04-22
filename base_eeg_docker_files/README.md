# Containerization 
Containerization is an alternative or companion to virtualization. It involves encapsulating or packaging up software and all its dependencies so that it can run uniformly and consistently on any infrastructure. This allows for developers to create and deploy applications faster and more securely. Moreover, this allows researchers to replicate each others analyses deterministically (computational replicability). The image built using the dockerfile has all the base functionality required for analysis, such as Python, MNE, Nipype, TensorFlow, Pandas, and more.  


## What is Docker?

Docker is a set of platform as a service products that use OS-level virtualization to deliver software in packages called containers. Containers are isolated from one another and bundle their own software, libraries, and configuration files. 

## What is a Docker Volume? 
Docker volumes are the preferred mechanism for persisting data generated 
by and used by Docker containers. While bind mounts are dependent on the 
directory structure and OS of the host machine, volumes are completely 
managed by Docker. Volumes have several advantages over bind mounts: 
* Volumes are easier to back up or migrate than bind mounts.
* Volumes on Docker Desktop have much higher performance than bind mounts from Mac and Windows hosts.
* Volumes can be more safely shared among multiple containers.

Volumes are often a better choice than persisting data in a container’s writable layer, because a volume does not increase the size of the containers using it, and the volume’s contents exist outside the lifecycle of a given container. 

As a default, you should use volume mounts instead of bind mounts.


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
   


## Docker Instructions

The image built using the dockerfile has all the base functionality required for analysis (python, mne, nipype, tensorflow, pandas etc.) you just need to set your own local directories yourself at this time in order to save work between sessions.


### How to use docker: 
1. Download and install Docker on your local PC: [https://docs.docker.com/get-docker/]()

2. Pull the latest Dockerfile & requirements.txt from the Github repo
 
3. While in the directory of the Dockerfile type the following in terminal to build the image, where imageName is the tag of the image to use in the future. The final command is the path at which the dockerfile is located, so if in location of the docker file, specify `.` (the current directory)
	
	`docker build -t imageName:version .
	`

4. After the docker image is built, it can be run by typing:

	`docker run -it imageName:version bash
	`
	
	See additional commands below to run Docker with a mapped directory and / or Jupyter enabled


### How to use a local directory with docker after building (*without* Jupyter / JupyterLab): 

##### If using Linux/MacOS: 

`docker run --rm -it -v $(PWD):/projects -w /projects dockerImage:Version bash 
`
##### If using Windows: 

`docker run --rm -it -v %cd%:/projects -w /projects dockerImage:Version bash 
`
### How to use a local directory with docker after building (*with* Jupyter / JupyterLab): 

#### Run docker: 

##### If using Linux/MacOS: 

`docker run --rm -it -v $(PWD):/projects -w /projects -p 5000:8888 dockerImage:version bash 
`
##### If using Windows: 

`docker run --rm -it -v %cd%:/projects -w /projects -p 5000:8888 dockerImage:version bash 
`
#### While in virtual machine, run the following to link ports: 

`jupyter lab --ip 0.0.0.0 --no-browser --allow-root
`

Access Jupyter notebooks by either
 
* Following link listed in terminal 

* Copying and pasting localhost:5000/lab in browser  
