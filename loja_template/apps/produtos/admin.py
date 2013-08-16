#-*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin

from models import Categoria as CategoriaProduto
from models import Produto

from modulos.utilidades.imagem import cropar_imagem_view
from actions.geral import publicar_action, despublicar_action

from development.widgets import CustomImageWidget

       
class ProdutoAdmin(admin.ModelAdmin):
    actions = [despublicar_action, publicar_action]
    despublicar_action.short_description = u"Despublicar Produtos selecionados"
    exclude = ['autor']
    formfield_overrides = {
        models.ImageField: {'widget': CustomImageWidget},
    }
    list_display = ['titulo', 'prioridade', 'publicado', 'autor', 'data_editado', 'data_criado', 'admin_imagem_thumbnail']
    list_filter = ['publicado', 'data_criado', 'autor']
    publicar_action.short_description = u"Publicar Produtos selecionados"
    search_fields = ['titulo']    
    search_fields_verbose = [u'Título']    

    def queryset(self, request):
        if request.user.is_superuser:
            qs = self.model._default_manager.get_query_set().all()
        else:   
            qs = self.model._default_manager.get_query_set().filter(autor = request.user)
        return qs    
    
    def response_add(self, request, obj, post_url_continue = "../%s/") :
        redirect = super(ProdutoAdmin, self).response_add(request, obj)
        obj.autor = request.user 
        obj.save()
        return redirect


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(CategoriaProduto)