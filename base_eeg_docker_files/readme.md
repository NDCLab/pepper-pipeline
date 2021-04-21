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
