import pycurl
import io
from urllib.parse import urlencode
import json
from sharedb_django import settings

fields = {
    'grant_type': settings.GRANT_TYPE,
    'username': 'jinyan',
    'password': '123456'
}

USERPWD = ':'.join((settings.CLIENT_ID, settings.CLIENT_SECRET))

response = io.BytesIO()
c = pycurl.Curl()

c.setopt(pycurl.URL, settings.TOKEN_URL)
c.setopt(pycurl.POST, 1)
c.setopt(pycurl.NOPROGRESS, 1)
c.setopt(pycurl.USERPWD, USERPWD)
c.setopt(pycurl.POSTFIELDS, urlencode(fields))
c.setopt(pycurl.MAXREDIRS, 50)
c.setopt(pycurl.TCP_KEEPALIVE, 1)
c.setopt(pycurl.USERAGENT, 'curl/7.52.1')
c.setopt(pycurl.WRITEFUNCTION, response.write)
c.perform()
httpString = json.loads(response.getvalue().decode('UTF-8'))
print(httpString['access_token'])
c.close()

