# Django
# Python
import json

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


def index(request):
    return render(request, 'iid/index.html')


def login(request):
    if request.method == 'POST':
        global CONN
        token = request.POST.get("token", None)
        try:
            CONN = DataHub(token)
            table_list = CONN.table_list
            data = {'ok': True, 'table_list': table_list}
        except RuntimeError:
            data = {'ok': False}

        return HttpResponse(json.dumps(data), content_type='application/json')


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