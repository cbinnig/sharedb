# DataHub integration

A set of wrapper Python scripts that reach out to the DataHub API to manage
upload, downloading, and sampling datasets.
The main class, located in `datahub.py`, requires an access token from Datahub's
OAuth2 API.
This should be done through the usual methods, such as those seen in the
frontend code in this project.

The `DataHub` class is able to get a user's info, query tables, get all rows
from a table, and retrieve a reservoir sample.

