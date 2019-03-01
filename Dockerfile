FROM python:3
ADD apiconnection.py /

RUN pip install oauthlib
RUN pip install requests_oauthlib
RUN pip install pandas
RUN pip install csv

CMD [ "python", "./apiconnection.py" ]
