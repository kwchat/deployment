FROM tensorflow/tensorflow:latest-gpu
RUN apt-get update && apt-get intall nginx
EXPOSE 80