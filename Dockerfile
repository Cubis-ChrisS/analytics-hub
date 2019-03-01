FROM python:3
ADD apiconnection.py /
ADD token.dat ./
ADD credits.dat ./

RUN pip install oauthlib
RUN pip install requests_oauthlib
RUN pip install pandas

CMD [ "python", "./apiconnection.py" ]
