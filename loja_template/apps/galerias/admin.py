#-*- coding: utf-8 -*-
from datetime import datetime
from django.conf import settings
from django.contrib import admin
from django.db.models import Q, signals
from forms import FormAdminGaleria, FormAdminArquivo
from models import Crop, Tamanho, Foto, Galeria, UploadArquivo, Categoria
from utilidades.imagem import cropar_imagem_view
from actions.geral import publicar_action

def post_save_noticia(signal, instance, sender, **kwargs):
    raise Exception("SIGNAL FUNCIONANDO")

class ArquivoUploadAdmin(admin.ModelAdmin):
    exclude = ['autor']
    list_display = ['titulo', 'autor', 'data_editado', 'data_criado', 'publicado', 'admin_tamanho']
    form = FormAdminArquivo
    fieldsets = (
        (None, {'fields':('titulo', 'usar_nome', 'arquivo', 'thumbnails', 'publicado')}),
        )

    def response_add(self, request, obj, post_url_continur="../%s/") :
        redirect = super(ArquivoUploadAdmin, self).response_add(request, obj)
        obj.processar_zip(request.user)
        for tamanho in Tamanho.objects.filter(padrao = True).all():
            if not tamanho in obj.thumbnails.all():
                obj.thumbnails.add(tamanho)
        obj.autor = request.user
        obj.save()
        return redirect

    def response_change(self, request, obj) :
        redirect = super(ArquivoUploadAdmin, self).response_change(request, obj)
        obj.processar_zip(request.user)
        obj.save()
        return redirect

    #Ixibirá apenas os uploads que o usuario criou caso ele não seja um superusuario.
    def queryset(self, request):
        if request.user.is_superuser:
            qs = self.model._default_manager.get_query_set().all()
        else:
            qs = self.model._default_manager.get_query_set().filter(autor = request.user)
        return qs

class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'titulo_slug':('titulo',)}

class FotoAdmin(admin.ModelAdmin) :
    actions = ["publicar_action"]
    exclude = ['autor', 'upload']
    fieldsets = (
        (None, {'fields':('titulo', 'titulo_slug', 'descricao', 'ordem', 'imagem', 'thumbnails', 'publicado')}),
        )
    list_display = ['titulo', 'publicado', 'autor', 'data_editado', 'data_criado', 'admin_tamanho', 'admin_thumbnail']
    list_display_links = ['titulo']
    list_editable = ["publicado"]
    list_filter = ['autor', 'data_criado', 'publicado']
    search_fields = ['titulo']
    prepopulated_fields = {'titulo_slug':('titulo',)}

    def response_add(self, request, obj, post_url_continue="../%s/") :
        redirect = super(FotoAdmin, self).response_add(request, obj)
        obj.criar_miniaturas()
        obj.autor = request.user
        obj.adicionar_miniaturas_padrao()
        obj.save()
        request.session['obj_crop'] = obj
        crops = Crop.objects.all()
        request.session['crops'] = crops
        return cropar_imagem_view(request, obj.imagem.name, redirect, POST_DATA = True, crops = crops)

    def response_change(self, request, obj) :
        redirect = super(FotoAdmin, self).response_change(request, obj)
        obj.criar_miniaturas()
        obj.save()
        if request.FILES.has_key('arquivo'):
            obj.criar_miniaturas()
            request.session['obj_crop'] = obj
            return cropar_imagem_view(request, obj.imagem.name, redirect, POST_DATA = True)
        else:
            return redirect

    #Ixibirá apenas as fotos que o usuario criou caso ele não seja um superusuario.
    def queryset(self, request):
        if request.user.is_superuser:
            qs = self.model._default_manager.get_query_set().all()
        else:
            qs = self.model._default_manager.get_query_set().filter(Q(autor = request.user) | Q(publico = True))
        return qs

class GaleriaAdmin(admin.ModelAdmin):
    form = FormAdminGaleria
    list_display = ['titulo', 'categoria', 'autor', 'data_editado', 'data_criado', 'publicado']
    list_filter = ['data_criado', 'publicado', 'autor']
    fieldsets = (
        (None, {'fields': ('titulo', 'titulo_slug', 'categoria', 'capa', 'fotos', 'arquivos', 'publicado')}),
        )
    filter_horizontal = ['fotos', 'arquivos']
    prepopulated_fields = {"titulo_slug": ("titulo",)}
    search_fields = ['titulo']

    def response_add(self, request, obj, post_url_continue = "../%s/"):
        retorno = super(GaleriaAdmin, self).response_add(request, obj)
        obj.adicionar_arquivos()
        obj.autor = request.user
        obj.save()
        if obj.capa:
            obj.criar_miniatura_capa()
        return retorno

    def response_change(self, request, obj):
        retorno = super(GaleriaAdmin, self).response_change(request, obj)
        obj.adicionar_arquivos()
        obj.save()
        if obj.capa:
            obj.criar_miniatura_capa()
        return retorno

    #Ixibirá apenas as galerias que o usuario criou caso ele não seja um superusuario.
    def queryset(self, request):
        if request.user.is_superuser:
            qs = self.model._default_manager.get_query_set().all()
        else:
            qs = self.model._default_manager.get_query_set().filter(Q(autor = request.user) | Q(publico = True))
        return qs

class TamanhoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'largura', 'altura', 'proporcional', 'padrao']

    def response_add(self, request, obj, post_url_continue = "../%s/"):
        redirect = super(TamanhoAdmin, self).response_add(request, obj)
        obj.adicionar_para_fotos()
        return redirect

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Foto, FotoAdmin)
admin.site.register(Galeria, GaleriaAdmin)
admin.site.register(Tamanho, TamanhoAdmin)
admin.site.register(UploadArquivo, ArquivoUploadAdmin)
admin.site.register(Crop)