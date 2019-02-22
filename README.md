# datahub

You want to develop some Python code to connect with the API of the SAC Hub.

Packages / dependencies:
- Python      (version 3.7.1)
- oauthlib    (version 3.0.0)
- requests    (version 2.21.0)


To do:
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
