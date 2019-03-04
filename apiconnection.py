# -*- coding: utf-8 -*-
"""
Created on Mo Feb 25 2019
LastModified on Mo Mar 04 2019

@author: Bram Buysschaert

25/02:
- Defining the ConnectSacHub class (v0.1)
- Defining the .connect() method (v0.1) and the relevant submethods:
    (.readCred(), .readToken(), .newToken, .writeToken(), .getClient(), .testClient(), .fetchXcsrf())
- Defining the .updateNewReportLov() method (v0.1; no workaround for timestamp issue)
- Defining part of the POST workflow to change live assets to draft asasets:
    (.changeLive2Draf(), .updateStatusDraft(), .deleteDraft(), .autoValidateDraft())

27/02:
- Switching from .updateNewReportLov() to .updateReportSuggestions() development
- Defining the .updateReportSuggestions() method (v0.1) and the revelant submethods:
    (.extractSuggestionsInfoStore(), .makeReportSuggestions(), .formatReportSuggestionsBody(), .pushReportSuggestions())
- Defined the .getAssetStructure() method, that returns the unique fieldIds and lovFieldIdsself.
    (Bug at the API side that these do not always match)
    (Used where applicable)

01/03:
- Trying to investigate how to interact with this code through Docker
    Most of the changes happened outside of this code
- Minor update to the .connect() method, since some functionality for error handling was missing.

04/03:
- Finishing the development of .pushReportSuggestions() and make it handle assets with no suggestions
- Defining the .formatReportSuggestionsClear() method
- Defining the .removeReportSuggestions() method (v0.1)
- Defining the .updateMailtoBody method (v0.1) and the relevant submethods
    (.pushMailtoBody(), .draftMailtoBody())
- Defining the .removeMailtoBody method (v0.1) and the relevant submethods
    (.pushMailtoBodyClear(), .draftMailtoBodyClear())
"""

# Include custom modules
from oauthlib import oauth2
from requests_oauthlib import OAuth2Session
import pandas as pd

# Include standard modules
import csv
import time, datetime
import sys



# Set the logging

import logging

# Create extra functionality

# Function to see status code
# Function to test status code
#


# Generate the class
class ConnectSacHub:
    """
    Class that provides the interaction with the SAC Hub API that you wish for this POC.
    It has various methods, that each have a specific function / purpose
    """
    def __init__(self, credFile, tokenFile):
        """Initialize the ConnectSacHub class"""
        self.credFile = credFile
        self.tokenFile = tokenFile
        self.cred = {}
        self.token = {}
        self.base = ''
        self.client = None
        self.xcsrf = ''
        self.headers = {'x-csrf-token': 'fetch', 'Content-Type': 'application/json'}
        self.currentTime = time.time()      #Get the current Unix time stamp (it is implied to be UTC) in seconds!

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
        try:
            self.getClient()      # Create oauth client
            # Test connection
            if self.testClient():
                print(f'\tConnection established with info from "{self.tokenFile}"')
                pass
            else:
                raise ValueError('Token Expired')
        except:
            self.newToken()      # Create new token
            self.writeToken()      # Write token out
            self.getClient()      # Create oauth client
            # Test connection
            if self.testClient():
                print(f'\tConnection established with updated token')
                pass
            else:
                raise SystemError('Could not create a login token!')
        # Give the user feedback on how long the token remains valid
        timediff_token = datetime.datetime.utcfromtimestamp(self.token['expires_at']) - datetime.datetime.utcfromtimestamp(self.currentTime)
        print('\tToken expires in {:.2f}h'.format(timediff_token.seconds / 3600))
        # Get a new X-CSRF-Token
        self.fetchXcsrf()

    def updateNewReportLov(self, timeDiffMax = 14.):
        """
        Update the NewReport lov for all assets in the SAC Hub store
        Assets are considered "new" when the last change happened less than timeDiffMax days ago!
        timeDiffMax: time difference in *days*
        """
        print('Updating the "NewReport" lov of your *live* store')
        self.getLiveStore()
        # Test the age of each report
        newAsset = []
        print('\tDANGER:Look into the code: explicit wrong equation for debugging!')
        for timeMod in self.lastModified: # Need explicit for-loop, since datetime does not allow for list input
            timediff = (datetime.datetime.utcfromtimestamp(self.currentTime) -
            datetime.datetime.utcfromtimestamp(timeMod)).days   # Could still use the hours to round up, but not enabled
            if timediff < 1: #WARNING WARNING WARNING FOR DEBUGGING AND DEVL ONLY
                newAsset.append('Yes')
            else:
                newAsset.append('No')
        print('!!!Functionality not fully implemented!!!')

    def updateReportSuggestions(self, assets='all', nSuggestions=3):
        """
        Go through the specified assets and hard-update their reportSuggestions
        This method ignores any pre-existing reportSuggestions.
        This method will hard-remove any existing reportSuggestions if it cannot create any suggestions during this execution.
        """
        print('Updating ReportSuggestions in the live store!')
        # Some bookkeeping for the functionality
        if assets == 'all':
            assets = self.assetid
        elif type(assets) != 'list':
            assets = [assets]
            # Format everything to strings
            for cc, asset in enumerate(assets):
                assets[cc] = str(asset)
        # Retrieve minimal information to make report suggestions
        df = self.extractSuggestionsInfoStore() # Should have functionality for assets keyword!
        # Loop over the assets and update them
        for assetId in assets:
            # Get the suggestions for the assetId
            df_sug = self.makeReportSuggestions(df, assetId, nSuggestions)
            # Push the suggestions to the store
            self.pushReportSuggestions(df_sug, assetId)

    def removeReportSuggestions(self, assets='all'):
        """
        Go through the specified assets and hard-remove their reportSuggestions
        """
        print('Removing ReportSuggestions in the live store!')
        # Some bookkeeping for the functionality
        if assets == 'all':
            assets = self.assetid
        elif type(assets) != 'list':
            assets = [assets]
            # Format everything to strings
            for cc, asset in enumerate(assets):
                assets[cc] = str(asset)
        # Loop over the assets and remove their reportSuggestions
        for assetId in assets:
            print(f'\tAsset {assetId}: removing suggestion(s)')
            # Copy asset from live to draft
            draftId = self.changeLive2Draft(assetId)
            # Format the body for the POST request
            body = self.formatReportSuggestionsClear(assetId, draftId)
            # Perform POST request
            r = self.client.post(self.base + 'api/v1/asset/draft/' + str(draftId),
                                headers = self.headers, json=body)
            # Test the reply of the POST request
            if r.ok:
                print(f'\t\tSuccessful POST for report suggestions clearing')
                self.autoValidateDraft(draftId)
            else:
                print(f'\t\tUnsuccessful POST for report suggestions clearing with status_code {r.status_code}')
                self.deleteDraft(draftId)

    def updateMailtoBody(self, assets='all'):
        """
        Go through the specified assets and hard-update their mailto urls
        This method will draft a subject header for the email and part of the body
        """
        print('Drafting emails subject and body in the live store!')
        # Some bookkeeping for the functionality
        if assets == 'all':
            assets = self.assetid
        elif type(assets) != 'list':
            assets = [assets]
            # Format everything to strings
            for cc, asset in enumerate(assets):
                assets[cc] = str(asset)
        # Loop over the assets and update them
        for assetId in assets:
            # Push the drafted email to the store
            self.pushMailtoBody(assetId)

    def removeMailtoBody(self, assets='all'):
            """
            Go through the specified assets and hard-update their mailto urls
            This method will remove any subject header for the email and the drafted body
            """
            print('Drafting emails subject and body in the live store!')
            # Some bookkeeping for the functionality
            if assets == 'all':
                assets = self.assetid
            elif type(assets) != 'list':
                assets = [assets]
                # Format everything to strings
                for cc, asset in enumerate(assets):
                    assets[cc] = str(asset)
            # Loop over the assets and update them
            for assetId in assets:
                # Push the drafted email to the store
                self.pushMailtoBodyClear(assetId)

    # =========================================================
    # Methods that are called by other methods for functionality
    # =========================================================
    def readCred(self):
        """Get the login credentials from the credFile"""
        # WARNING: no header allowed in input file!
        print(f'\tReading credentials file "{self.credFile}"')
        with open(self.credFile) as csvfile:
            reader = csv.reader(csvfile)
            self.cred = {rows[0]:rows[1] for rows in reader}
        # Get the base explicit for easier referencing
        self.base = self.cred['base_url']

    def readToken(self):
        """Get the access token from the tokenFile"""
        # WARNING: no header allowed in input file!
        print(f'\tReading token file "{self.tokenFile}"')
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
        print(f'Please following the following link and authorize to generate a token\n{authorization_url}')
        # Ask the response of the authorization request
        authorization_response = input('\nEnter the full callback / response URL from authorization\n')
        print('\tNow generating a token')
        # Fetch the token itself
        self.token = self.client.fetch_token(self.cred['token_url'], authorization_response=authorization_response, client_id=self.cred['client_id'],  client_secret=self.cred['client_secret'])

    def writeToken(self):
        """Write out the access token, because you generated a new token"""
        print(f'\tUpdating token file "{self.tokenFile}"')
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
        r = self.client.get(self.base + 'api/v1/profile')
        return r.ok

    def fetchXcsrf(self):
        """Fetch a new X-CSRF-token from a get request to the user profile and update the header"""
        print('\tFetching a new X-CSRF-Token')
        r = self.client.get(self.base + 'api/v1/profile', headers=self.headers)
        if r.ok:
            self.xcsrf = r.headers['x-csrf-token']
            self.headers['x-csrf-token'] = self.xcsrf
            print('\tX-CSRF-Token updated')

    def getLiveStore(self):
        """Retrieve the information of your live assets in your SAC Hub store through a GET request"""
        print('\tGETting *partial* information of your live store')
        r = self.client.get(self.base + 'api/v1/asset/recent', headers=self.headers)
        if r.ok:
            # Create a dictionary for the store
            self.store = {}
            for asset in r.json():
                self.store[str(asset['id'])] = asset
            self.assetid = self.store.keys()
        else:
            print(f'Your GET request was unsuccessful with status code {r.status_code}')

    def getAssetStructure(self):
        """Retrieve the full field, lovfield and lov structure of the asset layout"""
        print('\tGETting the information of your asset layout')
        # Warning: you do not get the different asset types, as there is currently only one type!
        # Get the fields
        rfield = self.client.get(self.base + 'api/v1/structure/field', headers=self.headers)
        # Get the lovfields
        rlovf = self.client.get(self.base + 'api/v1/structure/lovfield', headers=self.headers)
        # Get the lovs
        rlov = self.client.get(self.base + 'api/v1/structure/lov', headers=self.headers)
        # Successful GET requests
        if (rfield.ok) & (rlovf.ok) & (rlov.ok):
            fields, lovfs, lovs = {}, {}, {}
            # Include them to a nested dictionary
            for field in rfield.json():
                fields[field['title']] = {key: field[key] for key in ['id', 'title', 'multi']}
            for lovf in rlovf.json():
                lovfs[lovf['title']] = lovf #{key: lovf[key] for key in ['id', 'title', 'multi', 'lovId']}
            for lov in rlov.json():
                lovs[lov['title']] = {key: lov[key] for key in ['id', 'title']}
            self.structure = {'fields':fields, 'lovfields':lovfs, 'lovs':lovs}
        else:
            print(f'Your GET requests were unsuccessful with status code {rfield.status_code} (fields), {rlovf.status_code} (lovfields) and {rlov.status_code} (lovs)')

    def updateAssetLov(self, assetId, draftId, lovId, lovValue):
        """
        Update a lov for the asset with assetId and draftId through a POST request
        The lovId and new lovValue needs to be specified
        """
        print(f'\tPOSTing lov update to asset {assetId} with draftId {draftId}')
        print("Not fully implemented")

    def changeLive2Draft(self, assetId):
        """Change the status of a live asset to draft and return the draftId through a POST request"""
        print(f'\tPOSTing asset {assetId} from live to draft')
        r = self.client.post(self.base + 'api/v1/asset/' + str(assetId) + '/draft',
                            headers=self.headers, json={'status': 'draft'})
        if r.ok:
            draftId = r.json()['id']
            print(f'\t\tSuccessful POST; draft has draftId {draftId}')
            return draftId
        else:
            print(f'Your POST request was unsuccessful with status code {r.status_code}')
            print(self.base + 'asset/' + str(assetId) + '/draft')
            return None

    def updateStatusDraft(self, draftId, status='forReview'):
        """Change the status of a draft asset through a POST request"""
        if status not in ['forReview', 'draft', 'rejected', 'retired', 'live']:
            raise ValueError(f'Specify correct status to update draft {draftId}')
        print(f'\tPOSTing draft {draftId} to status {status}')
        r = self.client.post(self.base + 'api/v1/asset/draft/' + str(draftId) + '/status',
                            headers=self.headers, json={'status': status})
        if not r.ok:
            print(f'Your POST request was unsuccessful with status code {r.status_code}')

    def deleteDraft(self, draftId):
        """Delete a draft asset through a DELETE request"""
        print(f'\DELETEing draft {draftId}')
        r = self.client.delete(self.base + 'api/v1/asset/draft/' + str(draftId),
                            headers=self.headers)
        if not r.ok:
            print(f'Your DELETE request was unsuccessful with status code {r.status_code}')

    def autoValidateDraft(self, draftId, timeout=1.5):
        """Automatically update a draft from draft to forReview to live through a series of POST requests"""
        self.updateStatusDraft(draftId, status='forReview')
        time.sleep(timeout)
        self.updateStatusDraft(draftId, status='live')

    def extractSuggestionsInfoStore(self):
        """
        Extract the minimal information to make report suggestions from the local copy of the store that is stored at self.store
        The self.store was / should be retrieved earlier through self.getLiveStore()
        Returns a pandas dataframe with the minimal information needed to make suggestions
        """
        print('\tExtracting information for reportSuggestions from live store')
        # Empty dataframe to store the information to
        df = pd.DataFrame(index=self.assetid, columns=['assetType', 'assetTitle', 'viewCount', 'assetDomain', 'draftId'])
        # Get the id's for certain fields and lovs from the pre-loaded structure
        id_title = str(self.structure['fields']['Title']['id'])
        id_sugg = str(self.structure['fields']['Report Suggestions']['id'])
        id_domain = str(self.structure['lovfields']['Domain']['id'])
        # Loop over the assets in the store
        for assetId, asset in self.store.items():
            # Create dictionary with the information
            d = {'assetType': asset['type'],
                 'viewCount': asset['viewCount']}
            # Search in the fields for the title of the asset and old suggestions
            d['assetTitle'] = asset['fields'][id_title]['values'][0]['value'] # implicit assumption, but only one title allowed
            # Bug in SAP API that the following is not working
            # d['assetDomain'] = asset['lovFields'][id_domain]['values'][0]['value']  # implicit assumption, but only one domain allowed
            # Work around with a for-loop
            for key, lovField in asset['lovFields'].items():
                if lovField['title'] == 'Domain':
                    d['assetDomain'] = lovField['values'][0]['value']
            # Append the dictionary to the dataframe
            df.loc[assetId] = pd.Series(d) # .loc is important, otherwise you append to unknown columns!
        # Name the index of the dataframe
        df.index.name = 'assetId'
        return df

    def makeReportSuggestions(self, df, assetId, nSuggestions=3):
        """
        Create the suggestions of assets for the specified assetId using the assetDomain parameter
        df is the information retrieved through extractSuggestionsInfoStore
        assetId: unique assetId of the studied assets
        nSuggestions: the maximal amount of suggestions you are allowed to make
        """
        # Get the domain of your asset
        domain = df.at[assetId, 'assetDomain']
        # Select only the assets with the same domain
        df_ = df.loc[df['assetDomain'] == domain]
        # Sort these asset on viewCount
        df_ = df_.sort_values(by='viewCount', ascending=False)
        # Remove the entry with assetId
        df_ = df_.drop(assetId)
        # Return only the first nSuggestions entries
        return df_.head(nSuggestions)

    def formatReportSuggestionsBody(self, df, assetId, draftId):
        """Format the JSON body to update the suggestions of the asset with assetId"""
        # Get the information about the ReportSuggestions field from the structure
        #id_sugg = str(self.structure['fields']['Report Suggestions']['id'])
        id_sugg = "10"
        # Get the information of the current live asset (GET statement or lookup in self.store)
        asset = self.store[str(assetId)]
        # Create the "values" for the suggestions
        values = []
        # Loop over the suggestions and append the suggestions
        # url is from looking at the store
        # title is the title of the suggested asset
        for idx, sugg in df.iterrows():
            values.append({"value":{"title": sugg['assetTitle'],
                   "url": self.base + f"index.html?#/asset/{idx}",
                   "type": "external"}})
        # Format the body with the minimal requirements of the current live asset
        # 1 = Title (standard)
        # id_sugg = 10 = Report suggestions (custom)
        body = {"id":draftId,
                "assetId":int(assetId),
                "type":asset['type'],
                "fields":{
                    "1": {"values":[{"value":asset['fields']["1"]['values'][0]['value']}]},
                    id_sugg: {
                        "values": values}
                        }
                }
        return body

    def formatReportSuggestionsClear(self, assetId, draftId):
        """Format the JSON body to remove the suggestions of the asset with assetId"""
        # Get the information about the ReportSuggestions field from the structure
        #id_sugg = str(self.structure['fields']['Report Suggestions']['id'])
        id_sugg = "10"
        # Get the information of the current live asset (GET statement or lookup in self.store)
        asset = self.store[str(assetId)]
        # Create an empty "values" list for the suggestions
        values = []
        # Format the body with the minimal requirements of the current live asset
        # 1 = Title (standard)
        # id_sugg = 10 = Report suggestions (custom)
        body = {"id":draftId,
                "assetId":int(assetId),
                "type":asset['type'],
                "fields":{
                    "1": {"values":[{"value":asset['fields']["1"]['values'][0]['value']}]},
                    "10": {
                        "values": values}
                        }
                }
        return body

    def pushReportSuggestions(self, df_sug, assetId):
        """
        Make the suggestions for the specified assets and push these assets to the store
        It uses the minimal information retrieved through extractSuggestionsInfoStore, that should be called separetely and is stored in the dataframe "df"
        You can specify an assetId, a list of assets, or 'all' assets (default) to which you want to alter the store
        Warning: this function will alter your store!
        """
        # Test if you have any suggestions to make
        if len(df_sug) != 0:
            print(f'\tAsset {assetId}: was able to create {len(df_sug)} of suggestion(s)')
            # Copy asset from live to draft
            draftId = self.changeLive2Draft(assetId)
            # Format the body for the POST request
            body = self.formatReportSuggestionsBody(df_sug, assetId, draftId)
            # Perform POST request
            r = self.client.post(self.base + 'api/v1/asset/draft/' + str(draftId),
                                headers = self.headers, json=body)
            # Test the reply of the POST request
            if r.ok:
                print(f'\t\tSuccessful POST for report suggestions')
                self.autoValidateDraft(draftId)
            else:
                print(f'\t\tUnsuccessful POST for report suggestions with status_code {r.status_code}')
                self.deleteDraft(draftId)
        # No suggestions to make, so remove them (if any)
        else:
            print(f'\tAsset {assetId}: has no suggestion(s)')
            # Copy asset from live to draft
            draftId = self.changeLive2Draft(assetId)
            # Format the body for the POST request
            body = self.formatReportSuggestionsClear(assetId, draftId)
            # Perform POST request
            r = self.client.post(self.base + 'api/v1/asset/draft/' + str(draftId),
                                headers = self.headers, json=body)
            # Test the reply of the POST request
            if r.ok:
                print(f'\t\tSuccessful POST for report suggestions')
                self.autoValidateDraft(draftId)
            else:
                print(f'\t\tUnsuccessful POST for report suggestions with status_code {r.status_code}')
                self.deleteDraft(draftId)

    def pushMailtoBody(self, assetId):
        """Draft the information for the POST request and update the asset that resided in the live store"""
        print(f'\tAsset {assetId}: updating the mailto URL')
        # Copy asset from live to draft
        draftId = self.changeLive2Draft(assetId)
        # Draft the JSON body
        body = self.draftMailtoBody(assetId, draftId)
        # Perform POST request
        r = self.client.post(self.base + 'api/v1/asset/draft/' + str(draftId),
                            headers = self.headers, json=body)
        # Test the reply of the POST request
        if r.ok:
            print(f'\t\tSuccessful POST for mailto update')
            self.autoValidateDraft(draftId)
        else:
            print(f'\t\tUnsuccessful POST for mailto update with status_code {r.status_code}')
            self.deleteDraft(draftId)

    def pushMailtoBodyClear(self, assetId):
        """Draft the information for the POST request and update the asset that resided in the live store"""
        print(f'\tAsset {assetId}: updating the mailto URL')
        # Copy asset from live to draft
        draftId = self.changeLive2Draft(assetId)
        # Draft the JSON body
        body = self.draftMailtoBodyClear(assetId, draftId)
        # Perform POST request
        r = self.client.post(self.base + 'api/v1/asset/draft/' + str(draftId),
                            headers = self.headers, json=body)
        # Test the reply of the POST request
        if r.ok:
            print(f'\t\tSuccessful POST for mailto update')
            self.autoValidateDraft(draftId)
        else:
            print(f'\t\tUnsuccessful POST for mailto update with status_code {r.status_code}')
            self.deleteDraft(draftId)

    def draftMailtoBody(self, assetId, draftId):
        """Draft the email subject and body from the information in the asset and return the json body for the POST"""
        # Get the information of the current live asset (GET statement for complete information)
        r = self.client.get(self.base + f'api/v1/asset/{assetId}', headers=self.headers)
        if r.ok:
            asset = r.json()
        else:
            print(f'\t\tUnsuccessful POST to get asset {assetId} info with status_code {r.status_code}')
        # Get the asset title
        asset_title = asset['fields']["1"]['values'][0]['value']
        # Get the asset "Report Owner"
        for id, field in asset['fields'].items():
            if field['title'] == 'Report Owner':
                id_mailto = str(id)
        # Create a "values" list for the new mailto and retrieve the old values
        values_old = asset['fields'][id_mailto]['values']
        values_new = []
        # Loop over the old values and write out the new values
        for value in values_old:
            owner = value['value']['title']
            url = value['value']['url']
            # Test if any formatting happened to the mailto url
            if '?' in url:
                if 'subject' in url:
                    url = url.split('?subject')[0]
                elif 'body' in url:
                    url = url.split('?body')[0]
            # Generate the subject and body and append it to the url
            url += f'?subject={asset_title}&body=Dear {owner},%0AI have a question regarding your report.'
            # Note: "%0A" is the encoding for a newline
            # Replace any whitespaces with the correct encoding
            url.replace(' ', '%20')
            # Write out the value
            values_new.append({"value":{"title": owner,
                   "url": url,
                   "type": "external"}})
        # Format the body with the minimal requirements of the current live asset
        # 1 = Title (standard)
        # asset_title = (automatically retrieved)
        body = {"id":draftId,
                "assetId":int(assetId),
                "type":asset['type'],
                "fields":{
                    "1": {"values":[{"value":asset_title}]},
                    id_mailto: {
                        "values": values_new}
                        }
                }
        return body

    def draftMailtoBodyClear(self, assetId, draftId):
        """Remove the email subject and body from the information in the asset and return the json body for the POST"""
        # Get the information of the current live asset (GET statement for complete information)
        r = self.client.get(self.base + f'api/v1/asset/{assetId}', headers=self.headers)
        if r.ok:
            asset = r.json()
        else:
            print(f'\t\tUnsuccessful POST to get asset {assetId} info with status_code {r.status_code}')
        # Get the asset title
        asset_title = asset['fields']["1"]['values'][0]['value']
        # Get the asset "Report Owner"
        for id, field in asset['fields'].items():
            if field['title'] == 'Report Owner':
                id_mailto = str(id)
        # Create a "values" list for the new mailto and retrieve the old values
        values_old = asset['fields'][id_mailto]['values']
        values_new = []
        # Loop over the old values and write out the new values
        for value in values_old:
            owner = value['value']['title']
            url = value['value']['url']
            # Test if any formatting happened to the mailto url
            if '?' in url:
                if 'subject' in url:
                    url = url.split('?subject')[0]
                elif 'body' in url:
                    url = url.split('?body')[0]
            # Write out the value
            values_new.append({"value":{"title": owner,
                   "url": url,
                   "type": "external"}})
        # Format the body with the minimal requirements of the current live asset
        # 1 = Title (standard)
        # asset_title = (automatically retrieved)
        body = {"id":draftId,
                "assetId":int(assetId),
                "type":asset['type'],
                "fields":{
                    "1": {"values":[{"value":asset_title}]},
                    id_mailto: {
                        "values": values_new}
                        }
                }
        return body

if __name__ == '__main__':
    # Call the class to generate a token
    my_connection = ConnectSacHub('./credits.dat', './token.dat')
    # Connect the class to the SAC Hub
    my_connection.connect()
    # Get a copy of the live Store
    my_connection.getLiveStore()
    # Understand the structure of the store
    my_connection.getAssetStructure()
    # Update the report suggestions
    #my_connection.removeReportSuggestions()
    # Update the mailto urls
    my_connection.updateMailtoBody(assets='1')


    ###################
    #### DEBUGGING ####
    ###################
    """
    store = my_connection.store

    r = my_connection.client.get(my_connection.base + 'api/v1/asset/1', headers=my_connection.headers)
    asset = r.json()
    #for fieldId, field in asset['fields'].items():
    #    print(fieldId, field)
    for value in asset['fields']['5']['values']:
        print( value['value']['title'])
    """
