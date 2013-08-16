#-*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin

from models import Estado, Cidade, Localizacao


admin.site.register(Estado)
admin.site.register(Cidade)
admin.site.register(Localizacao)