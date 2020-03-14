FROM python:3.7.6-buster

RUN pip install numpy==1.17
RUN pip install scipy
RUN pip install pandas==1.0.0
RUN pip install matplotlib
RUN pip install nltk

RUN pip install dash
RUN pip install dash-renderer
RUN pip install dash-html-components
RUN pip install dash-bootstrap-components
RUN pip install dash-core-components
RUN pip install plotly==4.5.0
RUN pip install wordcloud

RUN pip install gunicorn

RUN useradd -m datascientist
USER datascientist

WORKDIR /home/datascientist/

RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader wordnet
RUN python -m nltk.downloader stopwords

# have to be edited
RUN git clone https://github.com/herrfeder/Udacity-Project-Recommendations-With-IBM-Webapp.git
WORKDIR /home/datascientist/Udacity-Project-Recommendations-With-IBM-Webapp

ENV ENVIRONMENT production

RUN echo '#!/bin/bash' > entrypoint.sh
RUN echo 'gunicorn --bind 0.0.0.0:8050 app.app:server' >> entrypoint.sh
RUN chmod +x entrypoint.sh


ENTRYPOINT ["/home/datascientist/Udacity-Project-Recommendations-With-IBM-Webapp/entrypoint.sh"]