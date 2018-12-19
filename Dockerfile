# super simple docker environment to allow for testing of microGRIDS
# build with tag of acep/microgrids
# $ docker build -t microgrids .
# run the latest tagged image
# $ docker run -it -v ${PWD}:/microgrids microgrids

FROM ubuntu:bionic

MAINTAINER Dayne Broderson <dayne@alaska.edu>

RUN apt-get update \
  && apt-get upgrade -y 

#RUN apt-get install -y python
#
#RUN conda install -y -c anaconda netcdf4
#
#VOLUME /microgrids
#WORKDIR /microgrids
#
#ENV PYTHONPATH="$PYTHONPATH:/microgrids/"
#CMD [ "/bin/bash" ]
