The image built using the code has all the base functionality required for analysis (python, mne, nipype, tensor flow, pandas etc.) you would just need to set your own local directories yourself at this time in order to save work between sessions.
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
finally you can use the browser jupyter by typing the url: localhost:8888/tree on your local browser