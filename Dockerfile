# super simple docker environment to allow for testing of microGRIDS
# build with tag of acep/microgrids
# $ docker build -t microgrids .
# run the latest tagged image
# $ docker run -it -v ${PWD}:/microgrids microgrids

FROM ubuntu:bionic

MAINTAINER Dayne Broderson <dayne@alaska.edu>

RUN apt-get update \
  && apt-get upgrade -y 

RUN apt-get install -y python3-h5netcdf python3-netcdf4 python3-pandas 

VOLUME /microgrids
WORKDIR /microgrids
ENV PYTHONPATH="$PYTHONPATH:/microgrids/"
# PYTHONPATH should be GBSTools top level

CMD [ "/bin/bash" ]
