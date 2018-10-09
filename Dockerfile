FROM continuumio/anaconda3

COPY . /microgrids
WORKDIR /microgrids

ENV PYTHONPATH="$PYTHONPATH:/microgrids/"

CMD [ "/bin/bash" ]
