#Build image starting with...
FROM python:3

MAINTAINER Seppe and Robin
#Mounts volume?
#ADD . /3dh

#Set working directory
WORKDIR /3dh

#Set environment variables
ENV FLASK_APP build3dh_app.py
ENV FLASK_RUN_HOST 0.0.0.0

#Copy python libraries required
COPY requirements.txt requirements.txt

#Install python libraries required 
RUN pip install -r requirements.txt

#Add image metadata to show the listening port of the container
EXPOSE 5000

#Copy current directory to image container directory
COPY . .

#CMD ['python', '3Deployement_v3.0.py']
CMD ['export FLASK_APP=build3dh_app.py']
CMD flask run --host 0.0.0.0
