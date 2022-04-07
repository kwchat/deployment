FROM tensorflow/tensorflow:latest-gpu
RUN apt-get update && apt-get install nginx
EXPOSE 80
