# Python
import json
import pycurl
import io
from urllib.parse import urlencode
from sharedb_django import settings

# Django
from django.http import HttpResponse
from django.shortcuts import render

# Bundles
from iid.bundle import HIPAABundle, FERPABundle
# DataHub
from iid.datahub import DataHub

# DataHub connections
CONN = None

# Data processing pipelines
PIPELINES = {
    'hipaa': HIPAABundle,
    'ferpa': FERPABundle,
}
PIPELINE = None


def get_token(username, password):
    fields = {
        'grant_type': settings.GRANT_TYPE,
        'username': username,
        'password': password
    }

    userpwd = ':'.join((settings.CLIENT_ID, settings.CLIENT_SECRET))

    response = io.BytesIO()
    c = pycurl.Curl()

    c.setopt(pycurl.URL, settings.TOKEN_URL)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.NOPROGRESS, 1)
    c.setopt(pycurl.USERPWD, userpwd)
    c.setopt(pycurl.POSTFIELDS, urlencode(fields))
    c.setopt(pycurl.MAXREDIRS, 50)
    c.setopt(pycurl.TCP_KEEPALIVE, 1)
    c.setopt(pycurl.USERAGENT, 'curl/7.52.1')
    c.setopt(pycurl.WRITEFUNCTION, response.write)
    c.perform()
    httpString = json.loads(response.getvalue().decode('UTF-8'))
    return httpString['access_token']


def auth(request):
    if request.method == 'GET':
        username = request.GET.get("username", None)
        password = request.GET.get("password", None)
        try:
            token = get_token(username, password)
            data = {'ok': True, 'token': token}
        except:
            data = {'ok': False}

        return HttpResponse(json.dumps(data), content_type='application/json')


def index(request):
    return render(request, 'iid/index.html')


def login(request):
    if request.method == 'POST':
        global CONN
        try:
            token = request.POST.get("token")
            CONN = DataHub(token)
            table_list = CONN.table_list
            data = {'ok': True, 'table_list': table_list}
        except RuntimeError:
            data = {'ok': False}

        response = HttpResponse(json.dumps(data), content_type='application/json')
        response.set_cookie('oauth_token', token)
        return response


def pipeline(request):
    if request.method == 'GET':
        data = {
            'ok': True,
            'pipelines': {k: v.description for k, v in PIPELINES.items()}
        }

        return HttpResponse(json.dumps(data), content_type='application/json')
    if request.method == 'POST':
        global PIPELINE
        pipeline_name = request.POST.get("pipeline")
        if pipeline_name in PIPELINES:
            PIPELINE = PIPELINES[pipeline_name].pipeline
            data = {
                'ok': True,
                'pipeline': pipeline_name
            }
        else:
            data = {
                'ok': False,
                'error': 'Pipeline {0} not found'.format(pipeline_name)
            }
        return HttpResponse(json.dumps(data), content_type='application/json')


def query(request):
    if request.method == 'POST':
        repo_name = request.POST.get("repoName")
        table_name = request.POST.get('tableName')
        sample_size = request.POST.get('sampleSize')
        if sample_size == "":
            table = CONN.get_all_rows(repo_name, table_name)
        else:
            table = CONN.get_sample(repo_name, table_name, int(sample_size))
            PIPELINE.add_data(table)
        data = {
            'ok': True,
            'table': PIPELINE.data
        }
        return HttpResponse(json.dumps(data), content_type='application/json')


def classify(request):
    if request.method == 'POST':
        ratings = PIPELINE.classify()
        data = {
            'ok': True,
            'ratings': ratings
        }
        return HttpResponse(json.dumps(data), content_type='application/json')


def filter(request):
    if request.method == 'POST':
        filters = {}
        for arg in request.POST.keys():
            filters[arg] = request.POST.get(arg)
        PIPELINE.filter(filters)
        data = {
            'ok': True,
            'table': PIPELINE.data
        }
        return HttpResponse(json.dumps(data), content_type='application/json')


def upload(request):
    if request.method == 'POST':
        table_name = request.POST.get('tableName')
        repo_name = request.POST.get('repoName')
        upload_table = request.POST.get('uploadTable')
        up_repo_name = request.POST.get('up_repo_name')
        CONN.upload_table(repo_name, table_name, upload_table, PIPELINE, up_repo_name)
        data = {
            'ok': True
        }
        return HttpResponse(json.dumps(data), content_type='application/json')