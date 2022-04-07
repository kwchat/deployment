FROM tensorflow/tensorflow:latest-gpu
RUN apt-get update && apt-get install -y nginx
EXPOSE 80
