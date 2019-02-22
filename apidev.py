# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 2019

@author: Bramb
"""

# Include packages
from oauthlib import oauth2
import requests_oauthlib # Currently not working
import logging
import sys

# Enable logging
log = logging.getLogger('oauthlib')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

# Start dev


if __name__ == '__main__':
    callback_url = 'https://localhost:8080/callback'
    authorize_url = 'https://oauthasservices-a4f6d560e.hana.ondemand.com/oauth2/api/v1/authorize'
    accestoken_url = 'https://oauthasservices-a4f6d560e.hana.ondemand.com/oauth2/api/v1/token'
    client_id = 'sac-hub-demo'
    client_secret = 'sac-hub-demo'
    help(oauth2.WebApplicationClient)
