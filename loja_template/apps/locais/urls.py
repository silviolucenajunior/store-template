#-*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns("modulos.locais.views",

    url(r'^$', 'locais_view', name = "lojas_view"),
)