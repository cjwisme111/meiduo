# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = 'contents'
urlpatterns = [
    path("",views.IndexView.as_view(),name='index')
]
