# datahub

You want to develop some Python code to connect with the API of the SAC Hub.


Code is developed with Python version 3.7.1 through an Anaconda installation.


Dependencies (i.e. packages / modules used):
- oauthlib            (version 3.0.0)
- requests-oauthlib   (version 1.0.0)
- requests            (version 2.21.0)
- logging             (version 0.5.1.2)
- time
- datetime


To do:
- Understand which Python package we need to use!!!
- Create Python code to test the link with the API.
- Create Python code to perform a GET request to the API.
- Investigate how you can get a token for the code.
- Investigate how you receive the X-CSRF-Token from the initial GET request.
- Create Python code to perform a POST request to the API

Functionality needed / wanted:
- Generate / Get X-CSRF-Token from reply header
- Generate login token from credentials (otherwise needs to be outsourced?)
- Retrieve all assets through Get request
- Post request to update "NewReport"
  -> Get the assets
  -> Test the assets
  -> If asset needs to change, move to draft
  -> Update draft
  -> Push draft to forValidation to live

Major issue:
- Flag API and non-API updates, so the code knows when to ignore the API updates for "NewReport".
- Many potential implementations possible.  Unclear which is the simplest to take.
