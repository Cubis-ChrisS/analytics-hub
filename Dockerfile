FROM python:3
ADD apiconnection.py /

RUN pip install pystrich

CMD [ "python", "./my_script.py" ]
