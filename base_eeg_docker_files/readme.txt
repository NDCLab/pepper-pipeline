The image built using the dockerfile has all the base functionality required for analysis (python, mne, nipype, tensor flow, pandas etc.) you just need to set your own local directories yourself at this time in order to save work between sessions.

How to use docker: 
    1) Download and install Docker on your local PC (https://docs.docker.com/get-docker/). 
    2) Pull the latest Dockerfile & requirements.txt from the Github repo
    3) While in the directory of the Dockerfile type the following in terminal to build the image:

        docker build -t imageName:version . 

    (imageName is how you will call the image in the future)

    4) After the docker image is built, it can be run by typing:

        docker run -it imageName:version bash


How to use a local directory with docker after building: 
    1a) If using Linux/MacOS: 

        docker run --rm -it -v $(PWD):/projects -w /projects dockerImage:Version bash 

    1b) If using Windows: 

        docker run --rm -it -v %cd%:/projects -w /projects dockerImage:Version bash 

How to enable in-browser jupyter with port access: 
    1) Run docker: 
        a) If using Linux/MacOS: 

            docker run --rm -it -v $(PWD):/projects -w /projects -p 5000:8888 dockerImage:version bash 

        b) If using Windows: 

            docker run --rm -it -v %cd%:/projects -w /projects -p 5000:8888 dockerImage:version bash 

    2) While in virtual machine, run the following to link ports: 

        jupyter notebook --ip 0.0.0.0 --no-browser --allow-root

    3) Access jupyter notebooks by 
        a) Following link listed in terminal 

        3) Copying and pasting localhost:5000/tree in browser  
