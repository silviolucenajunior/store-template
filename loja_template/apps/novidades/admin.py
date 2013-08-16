#-*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin

from models import Novidade
from utilidades.imagem import cropar_imagem_view
from actions.geral import publicar_action, despublicar_action

from development.widgets import CustomImageWidget


class NovidadeAdmin(admin.ModelAdmin):
    actions = [despublicar_action, publicar_action]
    despublicar_action.short_description = u"Despublicar Novidades selecionadas"
    exclude = ['autor']
    formfield_overrides = {
        models.ImageField: {'widget': CustomImageWidget},
    }
    list_display = ['titulo', 'prioridade', 'abrir_em','publicado', 'autor', 'data_editado', 'data_criado', 'admin_imagem_thumbnail']
    list_filter = ['publicado', 'data_criado', 'autor']
    publicar_action.short_description = u"Publicar Novidades selecionadas"
    search_fields = ['titulo']
    search_fields_verbose = [u'Título']

    class Media:
        js = [
            '/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            '/static/grappelli/tinymce_setup/tinymce_setup.js',
            ]

    def queryset(self, request):
        if request.user.is_superuser:
            qs = self.model._default_manager.get_query_set().all()
        else:
            qs = self.model._default_manager.get_query_set().filter(autor = request.user)
        return qs

    def response_add(self, request, obj, post_url_continue = "../%s/") :
        redirect = super(NovidadeAdmin, self).response_add(request, obj)
        obj.autor = request.user
        obj.save()
        return redirect
  #      obj.criar_miniaturas()
  #      request.session['obj_crop'] = obj
  #      redirect = redirect.__getitem__("Location")
  #      return cropar_imagem_view(request, obj.imagem.name, redirect, 627, 297, '2.11', POST_DATA = True, manter_original = True)

    def response_change(self, request, obj):
        redirect = super(NovidadeAdmin, self).response_change(request, obj)
        return redirect


admin.site.register(Novidade, NovidadeAdmin)