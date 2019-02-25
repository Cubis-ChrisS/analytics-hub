# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 2019

@author: Bramb
"""

# Include packages
from oauthlib import oauth2
from requests_oauthlib import OAuth2Session
import logging
import sys
"""
# Set the logging
import logging

# create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s; %(name)s; %(levelname)s; %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# 'application' code
logger.debug('debug message')
logger.info('info message')
logger.warning('warn message')
logger.error('error message')
logger.critical('critical message')

# Enable logging
log = logging.getLogger('oauthlib')
log.addHandler(logging.StreamHandler(sys.stdout))
"""
# Start devq


if __name__ == '__main__':
    redirect_uri = 'https://localhost:8080/callback'
    authorize_url = 'https://oauthasservices-a4f6d560e.hana.ondemand.com/oauth2/api/v1/authorize'
    accestoken_url = 'https://oauthasservices-a4f6d560e.hana.ondemand.com/oauth2/api/v1/token'
    client_id = 'sac-hub-demo'
    client_secret = 'sac-hub-demo'

    # Example comes from https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html
    # Follow WebApplication workflow!
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url(authorize_url)
    print(f'\n\n{authorization_url}\n')
    authorization_response = input('Enter the full callback URL\n')
    token = oauth.fetch_token(accestoken_url, authorization_response=authorization_response, client_id=client_id,  client_secret=client_secret)
    print(f'Token is {token}')
    #r = oauth.get('https://daikin-europe-nv.eu1.sapanalytics.cloud/hub/api/v1/asset/draft', headers=my_headers)
    r = oauth.get('https://daikin-europe-nv.eu1.sapanalytics.cloud/hub/api/v1/asset/draft')
    print(f'Status code = 200? {r.ok})
    print(f'Response is {r.json}')
    print(f'Explicit status code of response: {r.status_code})
