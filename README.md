### Welcome to the 3D house builder for Antwerp

To use the app, open terminal, make a new directory 3dh and clone the repository

mkdir 3dh

cd 3dh

git clone git@github.com:dr-robin/3dh.git

Then you can load the app via docker
(if you don't have docker install, follow the instructions here https://docs.docker.com/engine/install/ubuntu/)

Then in terminal you can start the docker container as follows:

docker-compose build

docker-compose up -d

docker ps -a

flask run

Open you browser at http://127.0.0.1:5000/

Enter an address in Antwerp and click submit to view a 3D plot of the building.


Note:
We tried to deploy to heroku but failed so far
https://deployement-3d-house.herokuapp.com/

have a great day
