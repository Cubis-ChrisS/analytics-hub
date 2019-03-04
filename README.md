# API connection to SAC Hub

This repository contains functionality to interact with the SAC Hub through their API.  All developed functionality is stored in the *ConnectSacHub* class in the *apiconnection.py* file / script.  Smaller Python scripts calling this class can then be used to demonstrate the developed functionality.

Code is developed with Python version 3.7.1 through an Anaconda installation.

### Dependencies
Non-standard Python modules:
- oauthlib            (version 3.0.0)
- requests-oauthlib   (version 1.0.0)
- requests            (version 2.21.0)
- logging             (version 0.5.1.2)
- pandas              (version 0.23.4)

Standard Python modules:
- time
- datetime
- csv

### Basic usage
Get the app
> import apiconnection as app

Initiate the app
> myapp = app.ConnectSacHub('./credits.dat', './token.dat')

Connect the app with the API
> myapp.connect()

Get a local copy of the SAC Hub store
> myapp.getLiveStore()

Perform functionality (e.g., update the reportSuggestions)
> myapp.updateReportSuggestions(assets='all')

### Credentials file

Contains the information of your API and client.  This is a csv-file hidden as a txt-file.  As long as the file and path is correctly specified, the extension of the file does not matter.  The actual content is stored in a Python dictionary.

Formatting (order is not important):

- base_url,https://your_store_here.sapanalytics.cloud/hub/
- authorize_url,https://authorize_here/oauth2/api/v1/authorize
- token_url,https://authorize_here/oauth2/api/v1/token
- client_id,client_id
- client_secret,client_secret
- redirect_uri,https://XXX/callback

### Token file

Contains the information of your three-legged OAuth2.0 token.  This file is not encrypted, but should benefit from encription.  The file was constructed so you do not have to authorize each access to the API.  This is a csv-file hidden as a txt-file.  As long as the file and path is correctly specified, the extension of the file does not matter.  The actual content is stored in a Python dictionary.

Formatting (order is not important):

- access_token,token_here
- token_type,Bearer
- expires_in,expires_in_x_seconds
- refresh_token,refresh_token_here
- expires_at,unix_time

### Nice to have

These are things that are nice to have, but need to be tested / developed further in the future

- Standard interaction with Python logging
- Enable containerization with Docker


### Comments

- self.getLiveStore method:  gets the information of your store from a GET request to *self.base + api/v1/asset/recent*.  However, you do not get the complete information from that asset.  Only the first three fields are returned and all lovFields.  In case you want to look further than the first three fields, you will need to go to *self.base + api/v1/asset/assetId*.  Examples of the wanted extra information is the reportSuggestions or the contactPerson.

- self.getAssetStructure method: gets the information of your layout per assetType from a get request to *self.base + api/v1/structure/field*, *self.base + api/v1/structure/lovfield* and *self.base + api/v1/structure/lov*.  However, the information from these requests contradict themselves.  Especially for the lovField Ids.  This is very likely a bug at the API side from SAC Hub.



### Known issues

- during the connection, it can seem that the code is hanging at the *Reading token file "./token.dat* step.  So far, the origin of this issue is unknown.  You just have to wait slightly longer for an established connection.
