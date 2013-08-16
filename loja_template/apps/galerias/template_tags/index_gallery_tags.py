#-*-coding: utf-8 -*-
from django.conf import settings
from django import template
from django.template import Context
from django.contrib import admin
from galerias.models import Tamanho, Galeria
from django.template.defaultfilters import slugify
register = template.Library()

#Devolve o caminho que aponta para a miniatura indicada da foto.
def pegar_miniatura(foto, nome_miniatura):
    try:
        miniatura = Tamanho.objects.get(titulo = nome_miniatura)
        nome_foto = foto.imagem.name[len(settings.INDEX_GALLERY_ROOT) - 4:]
        return "%s%sthumbnails/%s_%s" % (settings.MEDIA_URL, settings.INDEX_GALLERY_ROOT, slugify(miniatura.titulo), nome_foto)
    except Tamanho.DoesNotExist:
        return ""
register.simple_tag(pegar_miniatura)

def pegar_galeria(nome_galeria):
    galeria = Galeria.objects.get(nome = nome_galeria)
    variaveis = Context({'MEDIA_URL': settings.MEDIA_URL, 'galeria': galeria})
    return variaveis
register.inclusion_tag('galeria.html')(pegar_galeria)
