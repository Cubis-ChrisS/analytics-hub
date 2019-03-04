# API connection to SAC Hub

This repository contains functionality to interact with the SAC Hub through their API.  All developed functionality is stored in the class in the apiconnection.py file / script.  Smaller Python scripts calling this class can then be used to demonstrate the developed functionality.

Code is developed with Python version 3.7.1 through an Anaconda installation.

# Dependencies
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

# Basic usage
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
