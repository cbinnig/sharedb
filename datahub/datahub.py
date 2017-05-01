"""
A series of functions to connect to DataHub, upload files, and stream data from tables.
"""
import math
import random
import requests
import logging

# TODO: OAuth2 support
# This will most likely be rolled into the front-end rather than anything here.
# I'm still working on getting OAuth2 to work, so until then...

# DataHub base URL
BASE_URL = 'http://datahub-local.mit.edu/api/v1/'

class DataHub:
    def __init__(self, access_token):
        self.token = access_token
        self.info = self.get_user_info()

    def __default_params(self):
        """Generates default parameters for all calls to DataHub."""
        p = {}
        p['access_token'] = self.token
        return p

    def get_user_info(self):
        """Gets the user's info using the given testing token."""
        r = requests.get(BASE_URL + 'user/', params=self.__default_params())
        if r.status_code != requests.codes.ok:
            raise RuntimeError('Unable to return information about current user: {0}'.format(r.text))
        return r.json()

    def query_table(self, repo_name, query, rows_per_page=None, current_page=None):
        """
        Queries the given table with a query and optional rows per page and current page.
        Args:
            repo_name (str): The name of the repo to query. The repo root is found via user info.
            query (str): The query to execute.
            rows_per_page (int, optional): The number of rows per page. Defaults to 1000 (probably).
            current_page (int, optional): The current page; needed if we need more than one page.
        Output:
            Dict: The response from making the query.
        """
        params = self.__default_params()
        data = {'query': query}
        if rows_per_page is not None:
            data['rows_per_page'] = rows_per_page
        if current_page is not None:
            data['current_page'] = current_page

        r = requests.post(BASE_URL + 'query/{0}/{1}/'.format(self.info['username'], repo_name),
                          params=params, data=data)
        if r.status_code != requests.codes.ok:
            raise RuntimeError('Unable to perform query {0} on table {1}: {2}'.format(query, repo_name, r.text))
        return r.json()

    def get_all_rows(self, repo_name, table_name):
        """Selects all rows from the given table in the given repo."""
        rows = []
        current_page = 1
        has_next = True
        while has_next:
            res = self.query_table(repo_name, 'SELECT * FROM {0}.{1}'.format(repo_name, table_name), current_page=current_page)
            rows.extend(res['rows'])
            # Check to see if there are remaining rows
            if 'next_results_params' in res:
                current_page = res['next_results_params']['current_page']
            else:
                has_next = False
        return rows

    def get_sample(self, repo_name, table_name, n):
        """
        Returns a size n sample of the given table in the given repo.
        Implements a somewhat okay version of reservoir sampling.
        """
        rows = []
        current_page = 1
        has_next = True
        while has_next:
            res = self.query_table(repo_name, 'SELECT * FROM {0}.{1}'.format(repo_name, table_name), current_page=current_page)
            # Sample
            if len(rows) < n:
                rows.extend(res['rows'][:n - len(rows)])
                res['rows'] = res['rows'][n - len(rows):]
            if res['rows']:
                for row in res['rows']:
                    # Choose random index and sample probability
                    idx = random.random()
                    p = random.random()
                    if p < idx:
                        rows[math.floor(idx * n)] = row
            # Check to see if there are remaining rows
            if 'next_results_params' in res:
                current_page = res['next_results_params']['current_page']
            else:
                has_next = False
        return rows

    def get_table_schema(self, repo_name, table_name):
        """
        get table schema for the repo_name.table_name
        """
        params = self.__default_params()
        data = {}
        r = requests.get(BASE_URL + 'repos/{0}/{1}/tables/{2}'.format(self.info['username'], repo_name, table_name),
                          params=params, data=data)
        if r.status_code != requests.codes.ok:
            raise RuntimeError('Unable to get schema on table {0}.{1}'.format(repo_name, table_name))
        content = r.json()
        return content["columns"]

    def delete_table(self, repo_name, table_name):
        """
        Delete the table required
        """
        params = self.__default_params()
        r = requests.delete(BASE_URL + 'repos/{0}/{1}/tables/{2}'.format(self.info['username'], repo_name, table_name),
                          params=params)

    def upload_table(self, repo_name, table_name, upload_table, PIPELINE):
        """
        upload filterd table into the same repo
        :param repo_name: repo to input
        :param table_name: original table name
        :param upload_table: filtered table name
        :param PIPELINE: contains filtered data
        """
        table_schema = self.get_table_schema(repo_name, table_name)
        schema_dict = {}
        for item in table_schema:
            schema_dict[item['column_name']] = item['data_type']
        schema_list = []
        for column in PIPELINE.columns:
            tmp = column + ' ' + schema_dict[column]
            schema_list.append(tmp)
        schema = '(' + ','.join(schema_list) + ')'

        # if table exist, delete it first
        self.delete_table(repo_name, upload_table)

        # create table
        try:
            res = self.query_table(repo_name, 'CREATE TABLE {0}.{1}{2}'.format(repo_name, upload_table, schema))
        except Exception as e:
            logging.error('Uncaught exception when creating table: {e}'.format(e=e))

        # insert values
        num = len(PIPELINE.data[PIPELINE.columns[0]])
        result = []
        for i in range(num):
            tmp = []
            for key in PIPELINE.columns:
                tmp.append('NULL' if PIPELINE.data[key][i]==None else "'" + str(PIPELINE.data[key][i]) + "'")
            value = '(' + ','.join(tmp) + ')'
            result.append(value)
        result = ','.join(result)
        try:
            res = self.query_table(repo_name, 'INSERT INTO {0}.{1} VALUES {2}'.format(repo_name, upload_table, result))
        except Exception as e:
            logging.error('Uncaught exception when inserting table: {e}'.format(e=e))