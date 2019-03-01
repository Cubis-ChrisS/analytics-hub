# -*- coding: utf-8 -*-
"""
Created on Mo Feb 25 2019
LastModified on We Feb 27 2019

@author: Bram Buysschaert

25/02:
- Defining the ConnectSacHub class (v0.1)
- Defining the .connect() method (v0.1)
- Defining the .updateNewReport() method (v0.1; no workaround for timestamp issue)


"""

# Include packages
from oauthlib import oauth2
from requests_oauthlib import OAuth2Session
import csv
import time, datetime
import pandas as pd

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
        # Loop over the assets and update the assets
        #for asset, id, newAsset in zip(self.store, self.assetid, newAsset):
        #    lovFields = asset['lovFields'].items()
        #    for key_lovo, val_lovo in lovFields:
        #        for key_lovi, val_lovi in val_lovo.items():
        #            if val_lovi == 'New Report':
        #                print(key_lovo, key_lovi, val_lovi)
        #        print(key_lovo, val_lovo)

    def updateReportSuggestions(self, assets='all', nSuggestions=3):
        """
        Go through the store and test whether i) the report suggestions exist and ii) the report suggestions are correct
        If the tests fail, you update the report suggestions with new values (i.e., links)
        """
        # Retrieve minimal information to make report suggestions
        df_sug = self.extractSuggestionsInfoStore()
        # Perform suggestions for each asset and push them to the store
        self.pushReportSuggestions(df_sug, assets, nSuggestions)



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
        """Retrieve the full information of your live assets in your SAC Hub store through a GET request"""
        print('\tGETting the information of your live store')
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
        """Extract the minimal information to make report suggestions from the local copy of the store"""
        print('Extracting information for reportSuggestions from live store')
        # Empty dataframe to store the information to
        df = pd.DataFrame(index=self.assetid, columns=['assetType', 'assetTitle', 'viewCount', 'assetDomain', 'draftId', 'suggestionIds'])
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
            try:
                x = []
                for val in asset['fields'][id_sugg]:
                    x.append(val['value'])
                d['suggestionIds'] = x
            except:
                d['suggestionIds'] = []
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
        """Create the suggestions of assets for the specified assetId using the assetDomain parameter"""
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

    def formatReportSuggestions(self, df, assetId, draftId):
        """Format the JSON body to update the suggestions of the asset with assetId"""
        # Get the information about the ReportSuggestions field from the structure
        #id_sugg = str(self.structure['fields']['Report Suggestions']['id'])
        id_sugg = "10"
        # Get the information of the current live asset (GET statement or lookup in self.store)
        asset = self.store[str(assetId)]
        # Create the "values" for the suggestions
        values = []
        # Loop over the suggestions
        for idx, sugg in df.iterrows():
            values.append({"value":{"title": sugg['assetTitle'],
                   "url": self.base + f"index.html/#/asset/{idx}",
                   "type": "external"}})
        # Format the body with the minimal requirements of the current live asset
        body = {"id":draftId,
                "assetId":int(assetId),
                "type":asset['type'],
                "fields":{
                    "1": {"values":[{"value":'MijnTitelIsVandaagDit'}]},
                    "10": {
                        "values": values}
                        }
                }
        return body

    def pushReportSuggestions(self, df, assets='all', nSuggestions=3):
        """
        Make the suggestions for the specified assets and push these assets to the store
        It uses the minimal information retrieved through extractSuggestionsInfoStore, that should be called separetely
        You can specify an assetId, a list of assets, or 'all' assets (default) to which you want to alter the store
        Warning: this function will alter your store!
        """
        print('Updating ReportSuggestions in the live store!')
        # Some bookkeeping for the functionality
        if assets == 'all':
            assets = self.assetid
        elif type(assets) != 'list':
            assets = [assets]
        # Loop over all the to-be-updated assets
        for assetId in assets:
            # Create the new suggesions
            df_sug = self.makeReportSuggestions(df, assetId, nSuggestions)
            # Test if you have any suggestions to make
            if len(df_sug) != 0:
                print(f'Asset {assetId}: was able to create {len(df_sug)} of suggestion(s)')
                draftId = self.changeLive2Draft(assetId)
                body = self.formatReportSuggestions(df_sug, assetId, draftId)
                r = self.client.post(self.base + 'api/v1/asset/draft/' + str(draftId),
                                    headers = self.headers, json=body)
                if r.ok:
                    print(f'\tSuccesful POST to update the suggestions for asset {assetId}')
                else:
                    print(f'\tUnsuccesful POST command to update suggestions with status_code {r.status_code}')
            """
            # Test if new suggestions are the same as old suggestions
            -test-
            if False:
                # Format the json with the new suggestions
                -format-
                # Create a draft
                -draftId = xxx -
                # POST the new json
                -post-
                # Autovalidate
                -validate-
            """







if __name__ == '__main__':
    # Call the class to generate a token
    my_connection = ConnectSacHub('./credits.dat', './token.dat')
    my_connection.connect()
    my_connection.getLiveStore()
    my_connection.getAssetStructure()
    my_connection.updateReportSuggestions()
    #df = my_connection.extractSuggestionsInfoStore()
    #print(df)
