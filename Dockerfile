# super simple docker environment to allow for testing of microGRIDS
# build with tag of acep/microgrids
# $ docker build -t microgrids .
# run the latest tagged image
# $ docker run -it -v ${PWD}:/microgrids microgrids

FROM continuumio/anaconda3

RUN conda install -y -c anaconda netcdf4
RUN apt-get install netcdf4 hdf5

VOLUME /microgrids
WORKDIR /microgrids

ENV PYTHONPATH="$PYTHONPATH:/microgrids/"
CMD [ "/bin/bash" ]
