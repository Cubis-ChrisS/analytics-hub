FROM python:3
ADD apiconnection.py ./
ADD token.dat ./
ADD credits.dat ./
ADD updatesuggestions.py ./

RUN pip install oauthlib
RUN pip install requests_oauthlib
RUN pip install pandas

ENTRYPOINT python apiconnection.py

#CMD [ "python", "./apiconnection.py" ]
