from django.conf.urls import url
from . import views


app_name = 'iid'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/', views.login, name='login'),
    url(r'^pipeline/', views.pipeline, name='pipeline'),
    url(r'^query/', views.query, name='query'),
    url(r'^classify/', views.classify, name='classify'),
    url(r'^filter/', views.filter, name='filter'),
    url(r'^upload/', views.upload, name='upload')
]
