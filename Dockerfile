FROM tensorflow/tensorflow:latest-gpu
RUN apt-get update && apt-get install -y nginx git
RUN mkdir /opt/kwchat
RUN git clone https://github.com/kwchat/frontend.git /opt/kwchat/frontend
RUN git clone https://github.com/kwchat/backend.git /opt/kwchat/backend
RUN apt-get remove -y git && apt-get -y autoremove
EXPOSE 80
