from django.conf.urls import patterns, include, url
from management import views

urlpatterns = patterns('',

    url(r'^$', views.Management.as_view(), name='management'),

    url(r'^answers/country/(?P<country_iso>[\w\-]+)/$', views.AnswersByCountry.as_view(), name='country'),

    url(r'^answers/questions/$', views.AnswersByQuestion.as_view(), name='questions'),

    url(r'^answers/download/$', views.Download.as_view(), name='download'),

)
