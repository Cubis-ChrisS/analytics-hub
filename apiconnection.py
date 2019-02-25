# -*- coding: utf-8 -*-
"""
Created on Mo Feb 25 2019

@author: Bramb
"""

# Include packages
from oauthlib import oauth2
from requests_oauthlib import OAuth2Session
import logging
import sys
import csv

# Set the logging
import logging

# Create extra functionality

# Function to see status code
# Function to test status code
#


# Generate the class
class ConnectSacHub:
    """
    Class that provides all the interaction with the SAC Hub API that you need.
    It has various methods, that each have a specific function / purpose
    """
    def __init__(self, credFile, tokenFile):
        """Initialize the ConnectSacHub class"""
        self.credFile = credFile
        self.tokenFile = tokenFile
        self.cred = {}
        self.token = {}
        self.base = ''

    # =========================================================
    #Methods that you would call
    # =========================================================
    def connect(self):
        """
        Establish a connection through Python with the API of SAC Hub
        It uses the credFile and tokenFile as input and might generate a new token, if needed
        """
        print('Trying to establish a connection with the API')
        self.readCred()
        self.readToken()
        # Create oauth client
        self.getClient()
        # Test connection
        if self.testClient():
            print(f'Connection established with info from {self.tokenFile}')
            pass
        else:
            # Create new token
            self.newToken()
            # Write token out
            self.writeToken()
            # Create oauth client
            self.getClient()
            # Test connection
            if self.testClient():
                print(f'Connection established with updated token')
                pass
            else:
                raise SystemError('Could not create a login token!')

    # =========================================================
    # Methods that are called by other methods for functionality
    # =========================================================
    def readCred(self):
        """Get the login credentials from the credFile"""
        # WARNING: no header allowed in input file!
        print(f'\tReading credentials file {self.credFile}')
        with open(self.credFile) as csvfile:
            reader = csv.reader(csvfile)
            self.cred = {rows[0]:rows[1] for rows in reader}
        # Get the base explicit for easier referencing
        self.base = self.cred['base_url']

    def readToken(self):
        """Get the access token from the tokenFile"""
        # WARNING: no header allowed in input file!
        print(f'\tReading token file {self.tokenFile}')
        with open(self.tokenFile) as csvfile:
            reader = csv.reader(csvfile)
            self.token = {rows[0]:rows[1] for rows in reader}
        self.token['scope'] = [''] # Not explictly saved and likely not needed!
        self.token['expires_at'] = float(self.token['expires_at'])

    def newToken(self):
        """
        Update the access token, because the token from the tokenFile has expired or is unreadable
        Requires the user to go to the website, authorize the token and provide the response
        """
        self.client = OAuth2Session(client_id=self.cred['client_id'], redirect_uri=self.cred['redirect_uri'])
        authorization_url, state = self.client.authorization_url(self.cred['authorize_url'])
        # Ask the user to authorize with the created url (and their login cred)
        print(f'Please following the following link and authorize to generate a token\n\n{authorization_url}')
        # Ask the response of the authorization request
        authorization_response = input('\nEnter the full callback / response URL from authorization\n')
        print('\tNow generating a token')
        # Fetch the token itself
        self.token = self.client.fetch_token(self.cred['token_url'], authorization_response=authorization_response, client_id=self.cred['client_id'],  client_secret=self.cred['client_secret'])

    def writeToken(self):
        """Write out the access token, because you generated a new token"""
        print('\tUpdating token file {self.tokenFile}')
        with open(self.tokenFile, 'w', encoding = 'UTF-8', newline='') as file:
            writer = csv.writer(file)
            for key, value in self.token.items():
                if key != 'scope':
                    writer.writerow((key, value))

    def getClient(self):
        """Create the oauthlib client for the connection"""
        self.client = OAuth2Session(client_id=self.cred['client_id'], redirect_uri=self.cred['redirect_uri'],
                                    token=self.token)

    def testClient(self):
        """Test the oauthlib connection to the client with a get request to the user profile and return boolean for success"""
        r = self.client.get(self.base + 'profile')
        return r.ok

    #def xcsrf(self):
        # Fetch a new X-CSRF-token




if __name__ == '__main__':
    # Call the class to generate a token
    my_connection = ConnectSacHub('./credits.dat', './token.dat')
    my_connection.connect()
    # Peform update of newDraft
