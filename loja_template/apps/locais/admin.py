#-*- coding: utf-8 -*-
import os

from django.conf import settings
from django.db import models
from django.contrib import admin
from django.contrib.admin.actions import delete_selected

from models import Bairro, Cidade, Local
from modulos.utilidades.imagem import cropar_imagem_view
from actions.geral import publicar_action, despublicar_action

from development.widgets import CustomImageWidget

from models import Local, Bairro, Cidade

class LocalAdmin(admin.ModelAdmin):
    list_display = ["titulo", "bairro", "latitude", "longitude"]

    def response_add(self, request, obj, post_url_continue='../%s/'):
        response = super(LocalAdmin, self).response_add(request, obj)
        obj.pegar_coordenadas()
        obj.save()
        return response

    def response_change(self, request, obj):
        response = super(LocalAdmin, self).response_change(request, obj)
        obj.pegar_coordenadas()
        obj.save()
        return response

admin.site.register(Local, LocalAdmin)
admin.site.register(Bairro)
admin.site.register(Cidade)

       
