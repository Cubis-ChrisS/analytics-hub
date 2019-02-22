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

# Enable logging
log = logging.getLogger('oauthlib')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

# Start devq


if __name__ == '__main__':
    redirect_uri = 'https://localhost:8080/callback'
    authorize_url = 'https://oauthasservices-a4f6d560e.hana.ondemand.com/oauth2/api/v1/authorize'
    accestoken_url = 'https://oauthasservices-a4f6d560e.hana.ondemand.com/oauth2/api/v1/token'
    client_id = 'sac-hub-demo'
    client_secret = 'sac-hub-demo'

    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url(authorize_url)
    print(authorization_url)
    authorization_response = input('Enter the full callback URL')
    token = oauth.fetch_token(accestoken_url, authorization_response=authorization_response, client_id=client_id,  client_secret=client_secret)
    print(token)
